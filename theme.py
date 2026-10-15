"""Reguly.de-style theme for LetterEase.

Centralizes the color palette, typography, spacing, and control styling so
every screen and widget follows one consistent design, mirroring the layout
language of reguly.de: a light green-tinted background, dark navy text, teal
accents, pill buttons, rounded cards, and dashboard-style metric tiles. The
CSS is injected once per run via apply_theme(); render_nav(), render_hero(),
render_steps() and render_footer() draw the shared page chrome. Only static,
trusted markup is used here — user or letter text is never interpolated into
HTML.
"""
from pathlib import Path
from string import Template

import streamlit as st

PALETTE = {
    'page': '#f5f8f6',
    'navy': '#0e2240',
    'teal': '#14b8a6',
    'teal_hover': '#0d9488',
    'teal_tint': '#ccfbf1',
    'card': '#FFFFFF',
    'card_border': 'rgba(14, 34, 64, 0.10)',
    'text': '#0e2240',
    'text_secondary': '#4b5f79',
    'success': '#22c55e',
    'warning': '#f59e0b',
    'error': '#ef4444',
}

FONT_STACK = '-apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'

_BRAND_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<rect x="2.5" y="4.5" width="19" height="15" rx="3" stroke="#14b8a6" stroke-width="1.8"/>'
    '<path d="m4.5 7.5 7.5 6 7.5-6" stroke="#14b8a6" stroke-width="1.8"'
    ' stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

_SQUIGGLE_SVG = (
    '<svg class="le-squiggle" viewBox="0 0 220 14" preserveAspectRatio="none" aria-hidden="true">'
    '<path d="M3 10 C 30 2, 55 12, 80 7 S 130 3, 160 9 S 205 6, 217 8"'
    ' fill="none" stroke="#14b8a6" stroke-width="5" stroke-linecap="round"/></svg>'
)

_CSS = '''
/* ---------- base typography ---------- */
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  font-family: $font;
  color: $text;
}
[data-testid="stAppViewContainer"] { background: $page; }
::selection { background: rgba(20, 184, 166, 0.22); }
/* Streamlit's fixed top chrome must stay transparent over the sticky nav */
header[data-testid="stHeader"] { background: transparent !important; }

/* ---------- page container ---------- */
[data-testid="stMainBlockContainer"] {
  max-width: 1120px;
  margin: 0 auto;
  padding-top: 1.25rem;
  padding-bottom: 3rem;
}
[data-testid="stVerticalBlock"] { gap: 0.55rem; }

/* ---------- anchor targets (sticky nav offset) ---------- */
.le-anchor { scroll-margin-top: 5.5rem; }

/* ---------- sticky top navigation ---------- */
.le-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
  border: 1px solid $card_border;
  border-radius: 16px;
  padding: 10px 18px;
  margin-bottom: 20px;
  box-shadow: 0 1px 2px rgba(14, 34, 64, 0.05);
}
.le-nav-brand {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-size: 18px;
  font-weight: 700;
  color: $navy;
  text-decoration: none;
}
.le-nav-brand svg { width: 26px; height: 26px; }
.le-nav-links { display: flex; align-items: center; gap: 4px; flex: 1; justify-content: center; }
.le-nav-links a {
  padding: 8px 14px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  color: $text_secondary;
  text-decoration: none;
  transition: background-color 0.12s ease, color 0.12s ease;
}
.le-nav-links a:hover { background: $teal_tint; color: $navy; }
/* keep the CTA clear of Streamlit's fixed deploy/hamburger toolbar */
.le-nav-right { padding-right: 9rem; }
.le-nav-cta {
  display: inline-flex;
  align-items: center;
  background: $teal;
  color: #FFFFFF;
  text-decoration: none;
  border-radius: 9999px;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.12s ease;
}
.le-nav-cta:hover { background: $teal_hover; color: #FFFFFF; }

/* ---------- hero ---------- */
.le-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
  padding: 36px 0 44px;
}
.le-hero-text { flex: 1 1 58%; }
.le-hero-art { flex: 0 1 42%; display: flex; justify-content: center; }
.le-hero-art svg { width: 100%; max-width: 380px; height: auto; }
.le-hero h1 {
  font-size: clamp(2.6rem, 5vw, 3.5rem);
  font-weight: 500;
  line-height: 1.08;
  letter-spacing: -0.02em;
  color: $navy;
  margin: 0 0 18px;
}
.le-accent { color: $teal; position: relative; display: inline-block; }
.le-squiggle {
  position: absolute;
  left: 0;
  bottom: -10px;
  width: 100%;
  height: 10px;
  display: block;
}
.le-hero p {
  font-size: 17px;
  line-height: 1.6;
  color: $text_secondary;
  margin: 0 0 26px;
  max-width: 34rem;
}
.le-hero-ctas { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.le-btn-primary {
  display: inline-block;
  background: $teal;
  color: #FFFFFF;
  border-radius: 9999px;
  padding: 13px 26px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.12s ease;
}
.le-btn-primary:hover { background: $teal_hover; color: #FFFFFF; }
.le-btn-ghost {
  display: inline-block;
  background: transparent;
  color: $navy;
  border: 1px solid $navy;
  border-radius: 9999px;
  padding: 12px 25px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.12s ease, color 0.12s ease;
}
.le-btn-ghost:hover { background: $navy; color: #FFFFFF; }

/* ---------- how-it-works step cards ---------- */
.le-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.le-step {
  background: $card;
  border: 1px solid $card_border;
  border-radius: 16px;
  padding: 24px;
}
.le-step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background: $teal_tint;
  color: $teal_hover;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
}
.le-step h3 { font-size: 16px; font-weight: 600; color: $navy; margin: 0 0 8px; }
.le-step p { font-size: 14px; line-height: 1.55; color: $text_secondary; margin: 0; }

/* ---------- section labels (reguly-style headings) ---------- */
.le-section {
  font-size: 18px;
  font-weight: 600;
  color: $navy;
  margin-bottom: 10px;
}

/* ---------- dashboard-style metric tiles ---------- */
.le-metric {
  background: $card;
  border: 1px solid $card_border;
  border-radius: 16px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  height: 100%;
}
.le-metric-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: $text_secondary;
}
.le-metric-value { font-size: 22px; font-weight: 700; color: $navy; line-height: 1.2; }
.le-metric--ok { color: $success; }
.le-metric--warn { color: $warning; }
.le-metric--error { color: $error; }
.le-metric--teal { color: $teal_hover; }

/* ---------- content panels (bordered containers) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: $card;
  border: 1px solid $card_border !important;
  border-radius: 16px;
  padding: 16px 20px 18px !important;
}

/* ---------- pill buttons ---------- */
button[data-testid^="stBaseButton"] {
  border-radius: 9999px;
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  min-height: 44px;
  transition: background-color 0.12s ease, border-color 0.12s ease, color 0.12s ease;
}
button[data-testid^="stBaseButton"]:active { transform: translateY(1px); }

/* primary: teal */
button[data-testid="stBaseButton-primary"] {
  background-color: $teal !important;
  border: 1px solid $teal !important;
  color: #FFFFFF !important;
}
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primary"]:focus {
  background-color: $teal_hover !important;
  border-color: $teal_hover !important;
  color: #FFFFFF !important;
}

/* secondary: navy outline */
button[data-testid="stBaseButton-secondary"] {
  background-color: $card !important;
  border: 1px solid $navy !important;
  color: $navy !important;
}
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="stBaseButton-secondary"]:focus {
  background-color: $navy !important;
  border-color: $navy !important;
  color: #FFFFFF !important;
}

/* destructive: the Clear button is the only secondary button placed in a column */
[data-testid="stColumn"]:has([data-testid="stBaseButton-secondary"]) [data-testid="stBaseButton-secondary"] {
  background-color: $card !important;
  border: 1px solid $error !important;
  color: $error !important;
}
[data-testid="stColumn"]:has([data-testid="stBaseButton-secondary"]) [data-testid="stBaseButton-secondary"]:hover,
[data-testid="stColumn"]:has([data-testid="stBaseButton-secondary"]) [data-testid="stBaseButton-secondary"]:focus {
  background-color: $error !important;
  border-color: $error !important;
  color: #FFFFFF !important;
}

/* keyboard focus, visible on every control */
button:focus-visible,
[role="tab"]:focus-visible,
[role="radio"]:focus-visible,
[role="checkbox"]:focus-visible,
textarea:focus-visible,
input:focus-visible {
  outline: 2px solid $teal !important;
  outline-offset: 2px;
}

/* disabled */
button[data-testid^="stBaseButton"][disabled],
button[data-testid^="stBaseButton"][aria-disabled="true"] {
  opacity: 0.45 !important;
  cursor: not-allowed;
  transform: none;
}

/* ---------- input tabs ---------- */
[data-testid="stTabs"] [role="tablist"] { gap: 8px; border-bottom: none; }
[data-testid="stTabs"] button[data-testid="stTab"] {
  border-radius: 9999px;
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 500;
  color: $text_secondary;
  background: transparent;
}
[data-testid="stTabs"] button[data-testid="stTab"]:hover { color: $navy; background: $teal_tint; }
[data-testid="stTabs"] button[data-testid="stTab"][aria-selected="true"] {
  color: $navy;
  font-weight: 600;
  box-shadow: inset 0 -3px 0 0 $teal;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: $teal !important; }
[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

/* ---------- progress bar (compliance-score style) ---------- */
[data-testid="stProgress"] {
  background: $teal_tint;
  border-radius: 9999px;
  height: 10px;
}
[data-testid="stProgress"] [data-testid="stProgressValue"],
[data-testid="stProgress"] > div {
  background-color: $teal !important;
  border-radius: 9999px;
}

/* ---------- text inputs and text areas ---------- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
textarea {
  background-color: $card !important;
  color: $text !important;
  border: 1px solid rgba(14, 34, 64, 0.25) !important;
  border-radius: 10px;
  font-size: 14px !important;
  line-height: 1.5 !important;
  padding: 8px 10px !important;
}
[data-testid="stTextArea"] textarea:focus,
textarea:focus {
  border-color: $teal !important;
  box-shadow: 0 0 0 2px rgba(20, 184, 166, 0.25) !important;
  outline: none !important;
}
textarea:disabled,
textarea[readonly] {
  background-color: $page !important;
  color: $text_secondary !important;
  border-color: $card_border !important;
}

/* ---------- file uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
  background: $card !important;
  border: 1.5px dashed $teal !important;
  border-radius: 12px !important;
  min-height: 72px;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: $teal_hover !important;
  background: $teal_tint !important;
}

/* ---------- camera input ---------- */
[data-testid="stCameraInput"] {
  border: 1px solid $card_border;
  border-radius: 12px;
  overflow: hidden;
  max-width: 100%;
}

/* ---------- form labels and body text ---------- */
label {
  font-size: 13.5px !important;
  font-weight: 600;
  color: $text !important;
}
[data-testid="stMarkdownContainer"] p { font-size: 14px; }
pre { font-size: 13px; line-height: 1.55; }

/* ---------- alerts ---------- */
[data-testid="stAlert"] {
  border-radius: 12px;
  font-size: 13.5px;
}

/* ---------- footer ---------- */
.le-footer {
  margin-top: 48px;
  border-top: 1px solid $card_border;
  padding: 32px 0 8px;
}
.le-footer-grid { display: grid; grid-template-columns: 2fr 1fr 1.4fr 1.6fr; gap: 28px; }
.le-footer h4 {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: $navy;
  margin: 0 0 10px;
}
.le-footer-brand { font-size: 17px; font-weight: 700; color: $navy; margin: 0 0 6px; }
.le-footer p, .le-footer li { font-size: 13.5px; line-height: 1.6; color: $text_secondary; margin: 0; }
.le-footer ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.le-footer a { color: $text_secondary; text-decoration: none; }
.le-footer a:hover { color: $teal_hover; }
.le-footer-bottom {
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px solid $card_border;
  font-size: 12.5px;
  color: $text_secondary;
}

/* ---------- responsive ---------- */
@media (max-width: 800px) {
  .le-hero { flex-direction: column-reverse; gap: 20px; }
  .le-steps, .le-footer-grid { grid-template-columns: 1fr; }
  .le-nav-links { display: none; }
}

/* ---------- scrollbars ---------- */
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(14, 34, 64, 0.18);
  border-radius: 8px;
  border: 3px solid $page;
}
::-webkit-scrollbar-thumb:hover { background: rgba(14, 34, 64, 0.30); }
'''


def apply_theme():
    """Inject the shared stylesheet once per page load."""
    st.markdown(
        '<style>' + Template(_CSS).substitute(PALETTE, font=FONT_STACK) + '</style>',
        unsafe_allow_html=True,
    )


def anchor(target_id):
    """Anchor target for in-page navigation; ids only ever come from code literals."""
    st.markdown(f'<div id="{target_id}" class="le-anchor"></div>', unsafe_allow_html=True)


def render_nav():
    """Sticky top navigation: brand, anchor links, and a teal pill CTA."""
    st.markdown(
        f'<nav class="le-nav" id="top">'
        f'<a class="le-nav-brand" href="#top">{_BRAND_SVG}LetterEase</a>'
        f'<div class="le-nav-links">'
        f'<a href="#how-it-works">How it works</a>'
        f'<a href="#workspace">Workspace</a>'
        f'</div>'
        f'<div class="le-nav-right"><a class="le-nav-cta" href="#workspace">Explain a letter</a></div>'
        f'</nav>',
        unsafe_allow_html=True,
    )


def render_hero(subtitle, art='assets/hero.svg'):
    """Hero section: big headline with teal accent word, squiggly underline, pill CTAs."""
    art_path = Path(__file__).parent / art
    art_html = art_path.read_text(encoding='utf-8') if art_path.exists() else ''
    st.markdown(
        '<section class="le-hero">'
        '<div class="le-hero-text">'
        '<h1>German letters, explained in '
        f'<span class="le-accent">plain English{_SQUIGGLE_SVG}</span></h1>'
        f'<p>{subtitle}</p>'
        '<div class="le-hero-ctas">'
        '<a class="le-btn-primary" href="#workspace">Explain my letter</a>'
        '<a class="le-btn-ghost" href="#how-it-works">See how it works</a>'
        '</div>'
        '</div>'
        f'<div class="le-hero-art" aria-hidden="true">{art_html}</div>'
        '</section>',
        unsafe_allow_html=True,
    )


def render_steps():
    """Three 'how it works' cards, mirroring reguly.de's module cards."""
    st.markdown(
        '<div class="le-steps">'
        '<div class="le-step"><span class="le-step-num">1</span>'
        '<h3>Bring your letter</h3>'
        '<p>Type or paste the text, upload a document (PDF, Word, image and '
        'more), or take a picture of the page.</p></div>'
        '<div class="le-step"><span class="le-step-num">2</span>'
        '<h3>Review the text</h3>'
        '<p>Check the extracted text, fix any OCR slips, and remove personal '
        'details you do not want to send.</p></div>'
        '<div class="le-step"><span class="le-step-num">3</span>'
        '<h3>Get your explanation</h3>'
        '<p>Receive a plain-English explanation with a summary, required '
        'actions and important details — then download it.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )


def metric_tile(label, value, tone=''):
    """Dashboard-style stat tile; label, value and tone only ever come from code."""
    tone_class = f' le-metric--{tone}' if tone else ''
    st.markdown(
        f'<div class="le-metric"><span class="le-metric-label">{label}</span>'
        f'<span class="le-metric-value{tone_class}">{value}</span></div>',
        unsafe_allow_html=True,
    )


def render_footer():
    """Multi-column footer with static links and privacy notes."""
    st.markdown(
        '<footer class="le-footer">'
        '<div class="le-footer-grid">'
        '<div><p class="le-footer-brand">✉️ LetterEase</p>'
        '<p>German letters, explained in simple English.</p></div>'
        '<div><h4>Product</h4><ul>'
        '<li><a href="#workspace">Letter workspace</a></li>'
        '<li><a href="#how-it-works">How it works</a></li>'
        '</ul></div>'
        '<div><h4>Formats</h4><ul>'
        '<li>PDF, Word .docx, ODT, RTF</li>'
        '<li>TXT, Markdown, CSV</li>'
        '<li>JPG, PNG, WEBP, BMP, TIFF and camera photos</li>'
        '</ul></div>'
        '<div><h4>Privacy</h4><ul>'
        '<li>Only reviewed text is sent to TrustedTokens when you explain a letter.</li>'
        '<li>Letters and explanations are not stored or shared.</li>'
        '<li>AI output may contain mistakes — check it against the original.</li>'
        '</ul></div>'
        '</div>'
        '<div class="le-footer-bottom">© 2026 LetterEase AI · AI explanations may '
        'contain mistakes; verify dates, amounts and reference numbers against '
        'the original letter.</div>'
        '</footer>',
        unsafe_allow_html=True,
    )


def section_label(text):
    """Section heading used to group related controls."""
    st.markdown(f'<div class="le-section">{text}</div>', unsafe_allow_html=True)
