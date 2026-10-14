"""Run with: python -m streamlit run app.py"""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from extraction import EXTENSIONS, ExtractionError, extract
from core import MAX_CHARS, LetterEaseError, explain_letter, format_result

load_dotenv(Path(__file__).with_name('.env'), override=False)
st.set_page_config(page_title='LetterEase AI', page_icon='✉️', layout='centered')


def setting(name, default=''):
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        value = None
    return str(value if value is not None else os.getenv(name, default)).strip()


def clear():
    st.session_state.pop('result', None)
    st.session_state.pop('source', None)
    st.session_state.pop('extraction_notes', None)
    st.session_state['letter'] = ''
    st.session_state['upload_version'] = st.session_state.get('upload_version', 0) + 1

header_left, header_right = st.columns([2.6, 1])
with header_left:
    st.title('LetterEase AI')
    st.write('Understand your German letter in simple English.')
    st.caption('Type a letter, upload a document, or take a photo. Review the text before explaining it.')
with header_right:
    st.image(Path(__file__).with_name('assets') / 'hero.svg', width=220, output_format='SVG')
api_key = setting('TRUSTEDTOKENS_API_KEY')
model = setting('TRUSTEDTOKENS_MODEL', 'zai-org/GLM-5.3')
if not api_key or api_key.startswith('replace_'):
    st.info('Setup needed: add your TrustedTokens API key to .env locally or to Streamlit Secrets when hosted.')

def load_source(source, append=False, full_ocr=False):
    st.session_state.pop('result', None)
    try:
        with st.spinner('Reading the document…'):
            text, notes = extract(source.getvalue(), source.name, force_ocr=full_ocr)
        existing = st.session_state.get('letter', '')
        combined = (existing + '\n\n' + text) if append and existing.strip() else text
        if len(combined) > MAX_CHARS:
            raise ExtractionError('Combined text exceeds 30,000 characters. Clear the text or use a shorter document.')
        st.session_state['letter'] = combined
        st.session_state['extraction_notes'] = notes
        st.success('Text loaded below. Review it before selecting Explain letter.')
    except ExtractionError as exc:
        st.error(str(exc))

version = st.session_state.get('upload_version', 0)
method = st.radio('How would you like to enter your letter?', ['Type or paste', 'Upload a file', 'Take a picture'], horizontal=True)
if method == 'Upload a file':
    upload = st.file_uploader('Choose a document or image (up to 20 MB)', type=EXTENSIONS, key=f'upload_{version}')
    st.caption('PDF, Word .docx, ODT, RTF, TXT, Markdown, CSV, JPG, PNG, WEBP, BMP and TIFF. Convert older .doc files to .docx or PDF.')
    full_ocr = st.checkbox('Use full-page OCR for PDF (useful for scanned or mixed-content pages)')
    append = st.checkbox('Append to existing text', key='append_upload')
    if st.button('Read uploaded file', disabled=upload is None):
        load_source(upload, append, full_ocr)
elif method == 'Take a picture':
    st.caption('Allow camera access. Keep the whole page visible, flat and well lit. Capture and append each page of a multi-page letter.')
    photo = st.camera_input('Take a picture of the letter', key=f'camera_{version}')
    append = st.checkbox('Append this page to existing text', key='append_camera')
    if st.button('Read this picture', disabled=photo is None):
        load_source(photo, append)

for note in st.session_state.get('extraction_notes', []):
    st.warning(note)

letter = st.text_area('German letter — type, paste, or edit extracted text', key='letter', height=300, max_chars=MAX_CHARS)
st.caption('When you select Explain letter, the text is sent to TrustedTokens. Remove personal details you do not want to send. Files are processed on the app server. OCR uses temporary files which are removed after processing. Only the reviewed text is sent to TrustedTokens.')
left, right = st.columns([3, 1])
submitted = left.button('Explain letter', type='primary', disabled=not letter.strip())
right.button('Clear', on_click=clear)
if st.session_state.get('source') != letter:
    st.session_state.pop('result', None)
if submitted:
    st.session_state.pop('result', None)
    with st.spinner('Reading your letter…'):
        try:
            st.session_state['result'] = format_result(explain_letter(letter, api_key, model))
            st.session_state['source'] = letter
        except LetterEaseError as exc:
            st.error(str(exc))
if st.session_state.get('result'):
    # Plain text prevents model-generated links or HTML being rendered as active content.
    st.text(st.session_state['result'])
    st.download_button('Download explanation', st.session_state['result'], 'letter-explanation.txt', mime='text/plain')
    st.caption('Check dates, amounts and reference numbers against the original. AI output may contain mistakes.')
