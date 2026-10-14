"""Bounded file extraction and local German/English OCR."""
from io import BytesIO
from pathlib import Path
import os
import zipfile

MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 20
MAX_CHARS = 30000
EXTENSIONS = ['pdf', 'docx', 'odt', 'rtf', 'txt', 'md', 'csv', 'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tif', 'tiff']

class ExtractionError(Exception):
    pass


def checked(text):
    if len(text) > MAX_CHARS:
        raise ExtractionError('Extracted text exceeds 30,000 characters. Split the document; no text was loaded.')
    if not text.strip():
        raise ExtractionError('No readable text found. Try a clearer photo or type the text.')
    return text.strip()


def ocr(image):
    import pytesseract
    from PIL import ImageOps
    command = os.getenv('TESSERACT_CMD', '').strip()
    if command:
        pytesseract.pytesseract.tesseract_cmd = command
    try:
        languages = pytesseract.get_languages(config='')
        if not {'deu', 'eng'}.issubset(languages):
            raise ExtractionError('Install Tesseract German (deu) and English (eng) language data. See README.md.')
        image = ImageOps.exif_transpose(image).convert('RGB')
        return pytesseract.image_to_string(image, lang='deu+eng', timeout=45)
    except pytesseract.TesseractNotFoundError as exc:
        raise ExtractionError('OCR needs Tesseract installed. See README.md for local setup.') from exc
    except RuntimeError as exc:
        raise ExtractionError('OCR timed out. Use fewer pages or a smaller, clearer image.') from exc


def xml_document(data, extension):
    from defusedxml import ElementTree as ET
    with zipfile.ZipFile(BytesIO(data)) as archive:
        if sum(i.file_size for i in archive.infolist()) > MAX_BYTES:
            raise ExtractionError('The uncompressed document is too large.')
        names = archive.namelist()
        if extension == 'docx':
            main = 'word/document.xml'
            extras = sorted(n for n in names if n.startswith(('word/header', 'word/footer')) and n.endswith('.xml'))
            paths = [main] + extras
            paragraph_tag = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'
            text_tag = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'
            blocks = []
            for path in paths:
                root = ET.fromstring(archive.read(path))
                for p in root.iter(paragraph_tag):
                    blocks.append(''.join(n.text or '' for n in p.iter(text_tag)))
        else:
            root = ET.fromstring(archive.read('content.xml'))
            ns = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'
            blocks = [''.join(p.itertext()) for p in root.iter() if p.tag in (ns+'p', ns+'h')]
    return '\n'.join(blocks)


def extract(data, filename, force_ocr=False):
    if not data:
        raise ExtractionError('The file is empty.')
    if len(data) > MAX_BYTES:
        raise ExtractionError('Each file must be 20 MB or smaller.')
    extension = Path(filename).suffix.lower().lstrip('.')
    if extension not in EXTENSIONS:
        raise ExtractionError('Unsupported format. Save older Word .doc files as .docx or PDF first.')
    notes = []
    try:
        if extension in ('txt', 'md', 'csv'):
            try:
                text = data.decode('utf-8-sig')
            except UnicodeDecodeError:
                raise ExtractionError('Save this text file using UTF-8 encoding and try again.')
        elif extension == 'rtf':
            from striprtf.striprtf import rtf_to_text
            text = rtf_to_text(data.decode('cp1252'))
            notes.append('Embedded images in RTF are not read. Export to PDF to read image-based content.')
        elif extension in ('docx', 'odt'):
            text = xml_document(data, extension)
            notes.append('Review tables and headers carefully. Embedded images are not read; export to PDF and use full-page OCR if needed.')
        elif extension == 'pdf':
            import pypdfium2 as pdfium
            doc = pdfium.PdfDocument(data)
            try:
                if len(doc) > MAX_PAGES:
                    raise ExtractionError('PDFs may contain at most 20 pages. Split this file first.')
                pages = []
                used_ocr = False
                for i in range(len(doc)):
                    page = doc[i]
                    try:
                        textpage = page.get_textpage()
                        try:
                            page_text = textpage.get_text_range()
                        finally:
                            textpage.close()
                        if force_ocr or len(page_text.strip()) < 20:
                            width, height = page.get_size()
                            if width <= 0 or height <= 0:
                                raise ExtractionError('Invalid PDF page size.')
                            scale = min(3, (20_000_000 / (width * height)) ** 0.5)
                            bitmap = page.render(scale=scale)
                            try:
                                page_text = ocr(bitmap.to_pil())
                            finally:
                                bitmap.close()
                            used_ocr = True
                        if not page_text.strip():
                            raise ExtractionError(f'Page {i+1} has no readable text. Check this page; the document was not loaded.')
                        pages.append(page_text)
                        if sum(map(len, pages)) > MAX_CHARS:
                            raise ExtractionError('Extracted text exceeds 30,000 characters. Split this document.')
                    finally:
                        page.close()
                text = '\n\n'.join(pages)
                notes.append('Check page order and all text. For PDFs with both images and text, enable full-page OCR to read image-based content.')
                if used_ocr:
                    notes.append('OCR was used. Correct any misread dates, amounts and reference numbers before explaining.')
            finally:
                doc.close()
        else:
            from PIL import Image
            with Image.open(BytesIO(data)) as image:
                if getattr(image, 'n_frames', 1) > MAX_PAGES:
                    raise ExtractionError('Images may contain at most 20 frames/pages.')
                pages = []
                for i in range(getattr(image, 'n_frames', 1)):
                    image.seek(i)
                    if image.width * image.height > 25_000_000:
                        raise ExtractionError('Image exceeds 25 megapixels. Resize it and try again.')
                    page_text = ocr(image.copy())
                    if not page_text.strip():
                        raise ExtractionError(f'Image page {i+1} has no readable text. Take a clearer picture.')
                    pages.append(page_text)
                    if sum(map(len, pages)) > MAX_CHARS:
                        raise ExtractionError('Extracted text exceeds 30,000 characters.')
                text = '\n\n'.join(pages)
            notes.append('OCR was used. Correct any misread dates, amounts and reference numbers before explaining.')
        return checked(text), notes
    except ExtractionError:
        raise
    except ImportError as exc:
        raise ExtractionError('A file-reading dependency is missing. Install requirements.txt and restart.') from exc
    except Exception as exc:
        raise ExtractionError('Could not read this file. It may be damaged, password-protected, or unsupported. Try exporting to PDF or text.') from exc
