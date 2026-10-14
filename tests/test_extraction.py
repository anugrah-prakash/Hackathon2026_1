import ast
from io import BytesIO
from pathlib import Path
import unittest
from unittest.mock import patch
from PIL import Image
from extraction import extract, ExtractionError, MAX_BYTES

class ExtractionTests(unittest.TestCase):
    def test_utf8_preserves_values(self):
        text = 'Gebühr: 25,00 EUR\nFrist: 30.10.2026\nAz: STU-2026/00421'
        actual, _ = extract(text.encode('utf-8-sig'), 'letter.txt')
        self.assertEqual(actual, text)

    def test_input_limits(self):
        for data, name in [(b'', 'empty.txt'), (b'a' * (MAX_BYTES + 1), 'large.txt'),
                           (b'a' * 30001, 'long.txt'), (b'word', 'legacy.doc'),
                           (b'\xff', 'bad.txt')]:
            with self.subTest(name=name), self.assertRaises(ExtractionError):
                extract(data, name)

    @patch('extraction.ocr', return_value='Datum: 14.10.2026\nGebühr: 25,00 EUR')
    def test_camera_jpeg(self, ocr):
        buf = BytesIO()
        Image.new('RGB', (600, 800), 'white').save(buf, format='JPEG')
        text, notes = extract(buf.getvalue(), 'camera.jpg')
        self.assertIn('25,00 EUR', text)
        self.assertTrue(notes)
        ocr.assert_called_once()

    @patch('extraction.ocr', side_effect=['Page one 30.10.2026', 'Page two 25,00 EUR'])
    def test_scanned_multipage_pdf(self, ocr):
        buf = BytesIO()
        image = Image.new('RGB', (600, 800), 'white')
        image.save(buf, format='PDF', save_all=True, append_images=[image])
        text, _ = extract(buf.getvalue(), 'scan.pdf')
        self.assertEqual(text, 'Page one 30.10.2026\n\nPage two 25,00 EUR')
        self.assertEqual(ocr.call_count, 2)

    @patch('extraction.ocr', return_value='')
    def test_unreadable_image_rejected(self, ocr):
        buf = BytesIO()
        Image.new('RGB', (20, 20), 'white').save(buf, format='PNG')
        with self.assertRaises(ExtractionError):
            extract(buf.getvalue(), 'blank.png')

    def test_bad_pdf(self):
        with self.assertRaises(ExtractionError):
            extract(b'not a pdf', 'broken.pdf')

    def test_python_311_syntax(self):
        for path in Path('.').rglob('*.py'):
            if '.venv' not in path.parts:
                ast.parse(path.read_text(), feature_version=(3, 11))

if __name__ == '__main__':
    unittest.main()
