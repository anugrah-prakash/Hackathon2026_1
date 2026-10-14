"""Shared desktop-style theme for LetterEase.

Centralizes the color palette, typography, spacing, and control styling so
every screen and widget follows one consistent design. The CSS is injected
once per run via apply_theme(); app_header() and section_label() render the
shared chrome. Only static, trusted markup is used here — user or letter
text is never interpolated into HTML.
"""
from pathlib import Path
from string import Template

import streamlit as st

PALETTE = {
    'header': '#1E293B',
    'header_text': '#FFFFFF',
    'header_text_muted': '#94A3B8',
    'background': '#F1F5F9',
    'sidebar': '#E2E8F0',
    'panel': '#FFFFFF',
    'text': '#0F172A',
    'text_secondary': '#475569',
    'primary': '#2563EB',
    'primary_hover': '#1D4ED8',
    'secondary': '#E2E8F0',
    'secondary_hover': '#CBD5E1',
    'border': '#64748B',
    'divider': '#CBD5E1',
    'error': '#B91C1C',
    'success': '#15803D',
}

FONT_STACK = '-apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
BUTTON_HEIGHT = '34px'

_CSS = Template('''
/* ---------- base typography ---------- */
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  font-family: $font;
  color: $text;
}

/* ---------- compact, resize-safe workspace ---------- */
[data-testid="stMainBlockContainer"] {
  max-width: 940px;
  margin: 0 auto;
  padding-top: 1.1rem;
  padding-bottom: 2.5rem;
}
[data-testid="stVerticalBlock"] { gap: 0.55rem; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.45rem; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {
  border-right: 1px solid $divider;
}
[data-testid="stSidebarContent"] { padding-top: 1rem; }

/* ---------- app header ---------- */
.le-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  background: $header;
  border-radius: 10px;
  padding: 12px 20px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.20);
}
.le-header h1 {
  font-size: 19px;
  font-weight: 600;
  color: $header_text;
  margin: 0;
  line-height: 1.2;
}
.le-header-sub {
  color: $header_text_muted;
  font-size: 13px;
  margin: 4px 0 0;
  line-height: 1.45;
}
.le-header-art {
  flex: 0 0 auto;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 4px;
}
.le-header-art svg { width: 58px; height: auto; display: block; }

/* ---------- section labels ---------- */
.le-section {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: $text_secondary;
  border-bottom: 1px solid $divider;
  padding-bottom: 5px;
  margin-bottom: 8px;
}

/* ---------- content panels ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: $panel;
  border: 1px solid $divider !important;
  border-radius: 10px;
  padding: 14px 18px 16px !important;
}

/* ---------- buttons (shared base) ---------- */
button[data-testid^="stBaseButton"] {
  height: $button_height;
  min-height: $button_height;
  padding: 4px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 1px 1px rgba(15, 23, 42, 0.12);
  transition: background-color 0.12s ease, border-color 0.12s ease,
              box-shadow 0.12s ease;
}
button[data-testid^="stBaseButton"]:active { box-shadow: none; transform: translateY(1px); }

/* primary: blue */
button[data-testid="stBaseButton-primary"] {
  background-color: $primary !important;
  border: 1px solid $primary !important;
  color: $header_text !important;
}
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primary"]:focus {
  background-color: $primary_hover !important;
  border-color: $primary_hover !important;
}

/* secondary: neutral */
button[data-testid="stBaseButton-secondary"] {
  background-color: $secondary !important;
  border: 1px solid $secondary_hover !important;
  color: $text !important;
}
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:focus {
  background-color: $secondary_hover !important;
}

/* destructive: the Clear button is the only secondary button placed in a column */
[data-testid="stColumn"]:has([data-testid="stBaseButton-secondary"]) [data-testid="stBaseButton-secondary"] {
  background-color: $panel !important;
  border: 1px solid $error !important;
  color: $error !important;
  box-shadow: 0 1px 1px rgba(15, 23, 42, 0.08);
}
[data-testid="stColumn"]:has([data-testid="stBaseButton-secondary"]) [data-testid="stBaseButton-secondary"]:hover,
[data-testid="stColumn"]:has([data-testid="stBaseButton-secondary"]) [data-testid="stBaseButton-secondary"]:focus {
  background-color: $error !important;
  border-color: $error !important;
  color: $header_text !important;
}

/* keyboard focus, visible on every control */
button:focus-visible,
[role="radio"]:focus-visible,
[role="checkbox"]:focus-visible,
textarea:focus-visible,
input:focus-visible {
  outline: 2px solid $primary !important;
  outline-offset: 2px;
}

/* disabled */
button[data-testid^="stBaseButton"][disabled],
button[data-testid^="stBaseButton"][aria-disabled="true"] {
  opacity: 0.45 !important;
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
}

/* ---------- text inputs and text areas ---------- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
textarea {
  background-color: $panel !important;
  color: $text !important;
  border: 1px solid $border !important;
  border-radius: 6px;
  font-size: 14px !important;
  line-height: 1.5 !important;
  padding: 8px 10px !important;
}
[data-testid="stTextArea"] textarea:focus,
textarea:focus {
  border-color: $primary !important;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25) !important;
  outline: none !important;
}
textarea:disabled,
textarea[readonly] {
  background-color: $background !important;
  color: $text_secondary !important;
  border-color: $divider !important;
}

/* ---------- file uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
  background: $panel !important;
  border: 1.5px dashed $border !important;
  border-radius: 6px !important;
  min-height: 72px;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: $primary !important;
  background: #F8FAFC !important;
}

/* ---------- camera input ---------- */
[data-testid="stCameraInput"] {
  border: 1px solid $divider;
  border-radius: 6px;
  overflow: hidden;
}

/* ---------- form labels and body text ---------- */
label {
  font-size: 13.5px !important;
  font-weight: 600;
  color: $text !important;
}
[data-testid="stMarkdownContainer"] p { font-size: 14px; }
pre { font-size: 13px; line-height: 1.55; }

/* ---------- alerts (validation and status messages) ---------- */
[data-testid="stAlert"] {
  border-radius: 6px;
  font-size: 13.5px;
}

/* ---------- scrollbars ---------- */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: $divider;
  border-radius: 8px;
  border: 3px solid $background;
}
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }
''')


def apply_theme():
    """Inject the shared stylesheet once per page load."""
    st.markdown(
        '<style>' + _CSS.substitute(PALETTE, font=FONT_STACK, button_height=BUTTON_HEIGHT) + '</style>',
        unsafe_allow_html=True,
    )


def app_header(title, subtitle, art='assets/hero.svg'):
    """Dark desktop-style header bar with the app illustration on the right."""
    art_path = Path(__file__).parent / art
    art_html = art_path.read_text(encoding='utf-8') if art_path.exists() else ''
    st.markdown(
        f'<header class="le-header">'
        f'<div class="le-header-text"><h1>{title}</h1>'
        f'<p class="le-header-sub">{subtitle}</p></div>'
        f'<div class="le-header-art" aria-hidden="true">{art_html}</div>'
        f'</header>',
        unsafe_allow_html=True,
    )


def section_label(text):
    """Small uppercase section heading used to group related controls."""
    st.markdown(f'<div class="le-section">{text}</div>', unsafe_allow_html=True)
