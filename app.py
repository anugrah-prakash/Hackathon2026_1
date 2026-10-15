"""Run with: python -m streamlit run app.py"""
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from theme import (apply_theme, render_nav, render_hero, render_steps,
                   render_footer, section_label, metric_tile, anchor)
from extraction import EXTENSIONS, ExtractionError, extract
from core import MAX_CHARS, LetterEaseError, explain_letter, format_result

load_dotenv(Path(__file__).with_name('.env'), override=False)
st.set_page_config(page_title='LetterEase AI', page_icon='✉️', layout='wide')
apply_theme()


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

api_key = setting('TRUSTEDTOKENS_API_KEY')
model = setting('TRUSTEDTOKENS_MODEL', 'zai-org/GLM-5.3')
api_ready = bool(api_key) and not api_key.startswith('replace_')

# --- Top navigation and hero (reguly.de-style page chrome) ---
render_nav()
render_hero('Understand your German letter in simple English. '
            'Type a letter, upload a document, or take a photo. Review the text before explaining it.')

# --- How it works ---
anchor('how-it-works')
section_label('How it works')
render_steps()

# --- Workspace: status metrics (compliance-score style) ---
# Note: values are read before the widgets below render, so tiles refresh on
# the next interaction after a change (tab switches do not re-run the script).
anchor('workspace')
section_label('Your letter workspace')
letter_len = len(st.session_state.get('letter', ''))
has_result = bool(st.session_state.get('result'))
cols = st.columns(3)
with cols[0]:
    metric_tile('Setup', 'Configured' if api_ready else 'Setup needed', 'ok' if api_ready else 'warn')
with cols[1]:
    metric_tile('Letter text', f'{letter_len:,} / {MAX_CHARS:,}', 'teal')
with cols[2]:
    metric_tile('Explanation', 'Ready' if has_result else 'Pending', 'ok' if has_result else '')
st.progress(min(int(letter_len * 100 / MAX_CHARS), 100) if letter_len else 0)
if not api_ready:
    st.info('Setup needed: add your TrustedTokens API key to .env locally or to Streamlit Secrets when hosted.')
else:
    st.success('API key configured.')

version = st.session_state.get('upload_version', 0)

# --- Input methods: tabs replace the old sidebar radio; extraction stays
# button-driven, and clear() remounts the widgets with fresh keys. ---
section_label('Bring your letter')
tab_paste, tab_upload, tab_photo = st.tabs(['Type or paste', 'Upload a file', 'Take a picture'])
with tab_paste, st.container(border=True):
    st.caption('Type or paste your German letter directly into the editor below. You can also mix methods: '
               'read a document or photo first, then edit the combined text.')
with tab_upload, st.container(border=True):
    upload = st.file_uploader('Choose a document or image (up to 20 MB)', type=EXTENSIONS, key=f'upload_{version}')
    st.caption('PDF, Word .docx, ODT, RTF, TXT, Markdown, CSV, JPG, PNG, WEBP, BMP and TIFF. Convert older .doc files to .docx or PDF.')
    full_ocr = st.checkbox('Use full-page OCR for PDF (useful for scanned or mixed-content pages)')
    append_upload = st.checkbox('Append to existing text', key='append_upload')
    if st.button('Read uploaded file', disabled=upload is None,
                 help='Extract text from the selected file into the editor.'):
        load_source(upload, append_upload, full_ocr)
with tab_photo, st.container(border=True):
    st.caption('Allow camera access. Keep the whole page visible, flat and well lit. Capture and append each page of a multi-page letter.')
    photo = st.camera_input('Take a picture of the letter', key=f'camera_{version}')
    append_camera = st.checkbox('Append this page to existing text', key='append_camera')
    if st.button('Read this picture', disabled=photo is None,
                 help='Extract text from the captured photo into the editor.'):
        load_source(photo, append_camera)

# --- Workspace: letter editor ---
with st.container(border=True):
    section_label('Letter text')
    for note in st.session_state.get('extraction_notes', []):
        st.warning(note)
    letter = st.text_area('German letter — type, paste, or edit extracted text', key='letter', height=320, max_chars=MAX_CHARS)
    st.caption('When you select Explain letter, the text is sent to TrustedTokens. Remove personal details you do not want to send. Files are processed on the app server. OCR uses temporary files which are removed after processing. Only the reviewed text is sent to TrustedTokens.')

# --- Workspace: actions ---
with st.container(border=True):
    section_label('Actions')
    left, right = st.columns([3, 1])
    submitted = left.button('Explain letter', type='primary', disabled=not letter.strip(),
                           help='Send the reviewed text to TrustedTokens for a plain-English explanation.')
    right.button('Clear', on_click=clear,
                 help='Clear the letter text and the current explanation.')

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

# --- Workspace: explanation ---
if st.session_state.get('result'):
    with st.container(border=True):
        section_label('Explanation')
        # Plain text prevents model-generated links or HTML being rendered as active content.
        st.text(st.session_state['result'])
        st.download_button('Download explanation', st.session_state['result'], 'letter-explanation.txt', mime='text/plain',
                           help='Save the explanation as a plain-text file.')
        st.caption('Check dates, amounts and reference numbers against the original. AI output may contain mistakes.')

# --- Footer ---
render_footer()
