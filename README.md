# LetterEase AI

A Streamlit app for explaining German official letters in simple English.
Written for Python 3.11.4. Type/paste a letter, upload a supported document, or take a camera photo. Review and edit extracted text before explaining it.
The explanation has exactly three sections: SUMMARY, ACTION REQUIRED, and
IMPORTANT DETAILS. The API returns JSON; the app validates its structure and
renders the three headings itself. This does not guarantee factual accuracy:
check the explanation against the original letter.

## Included files

- `app.py`: Streamlit interface, text import, download and clear controls.
- `core.py`: prompt, TrustedTokens API request, validation and error handling.
- `extraction.py`: document extraction and German/English OCR.
- `packages.txt`: Tesseract and language packages for Streamlit Cloud.
- `.env`: local configuration with a placeholder key, not a real credential.
- `.env.example`: safe configuration template for Git.
- `requirements.txt`: pinned Python dependencies.
- `.streamlit/config.toml`: theme and upload settings.
- `.streamlit/secrets.toml.example`: hosted secret configuration example.
- `.vscode/launch.json`: VS Code debug configuration.
- `.gitignore`: excludes real secrets and local environments.
- `sample_letter.txt`: fictional letter for testing.
- `tests/test_core.py`: mocked integration and validation tests.

## 1. Run in VS Code

Extract the ZIP. Open the inner `letterease` folder in VS Code, so `app.py`
is directly inside the folder you opened. Install the Microsoft Python and
Python Debugger extensions. Install Python 3.11.4 if you need that exact version.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3.11 -m venv .venv
.venv/bin/python --version
.venv/bin/python -m pip install -r requirements.txt
```

Check the printed version is 3.11.4 if exact patch compatibility is required.
In VS Code, run **Python: Select Interpreter** and select `.venv`.
Edit the included `.env` file:

```dotenv
TRUSTEDTOKENS_API_KEY=your_actual_trustedtokens_key
TRUSTEDTOKENS_MODEL=zai-org/GLM-5.3
```

Use a model ID available to your TrustedTokens account. The default above is
an example from the provider's documentation, not a guarantee of account access.
The model must support JSON object output. Restart the app after changing `.env`.
Existing environment variables override `.env`; Streamlit Secrets take priority
over both. No real API key is included in this project.

Start on Windows:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Start on macOS / Linux:

```bash
.venv/bin/python -m streamlit run app.py
```

Open the local URL shown in the terminal, usually http://localhost:8501.
Alternatively select **LetterEase: Streamlit** in VS Code Run and Debug, then F5.

## 2. Test

Select **Upload a file**, import `sample_letter.txt`, click **Read uploaded file**, review the text, then select **Explain letter**.
The response should preserve `14.10.2026`, `30.10.2026`, `05.11.2026`,
`25,00 EUR`, and `STU-2026/00421`. It should identify the document request and
payment deadline, recognize the fictional test label, and not invent bank details
or claim payment was made. Reading a letter does not establish authenticity.

Run offline mocked tests using your virtual environment's Python:

```bash
python -m unittest discover -s tests -v
```

The app rejects empty input, letters over 30,000 characters, malformed responses,
and incomplete API completions. It provides safe errors for authentication,
quota, connection and timeout failures without displaying provider response bodies.
No automatic API retries occur. A manual retry can incur another charge.

## 3. Deploy on Streamlit Community Cloud

1. Create a GitHub repository with the project files at its root. Keep `.env`,
   `.venv`, and `.streamlit/secrets.toml` out of Git. The included `.gitignore`
   handles them when using Git; do not manually upload your real `.env`.
2. In Streamlit Community Cloud, create an app and select the repository, branch,
   and `app.py` as the entrypoint.
3. Select Python 3.11 in Advanced settings if available. Community Cloud manages
   Python patch versions; it does not guarantee exactly 3.11.4.
4. Paste the following into the Secrets field, with your real key:

```toml
TRUSTEDTOKENS_API_KEY = "your_actual_trustedtokens_key"
TRUSTEDTOKENS_MODEL = "zai-org/GLM-5.3"
```

5. Deploy. Streamlit installs `requirements.txt`. Test with the fictional letter.

The app uses the deployment owner's key. Anyone who can access the deployed app
can make billable API requests with it. Use private access for initial testing;
this starter app does not implement authentication or a shared rate limiter.

## Data and scope

Letter text is sent to TrustedTokens only after clicking Explain letter. The app
does not persist letters or explanations or cache them across users. Uploaded files
are processed on the app server. Tesseract uses temporary image/text files that its
wrapper removes after processing; temporary files are not durable storage.
Input and results remain in the browser/Streamlit session until cleared or the
session ends. Clear removes the app's current input and result; it cannot delete
data already received by the API provider. Consult the provider's own data terms.

This version accepts typed text, PDFs (including scans), Word DOCX, ODT, RTF,
UTF-8 TXT/Markdown/CSV, PNG/JPEG/WEBP/BMP/TIFF, and camera photos. It does not
check authenticity, calculate legal deadlines, or execute payments. Keep all
pages of a letter together. Older Word DOC files must be converted to DOCX or PDF. The app asks the model to preserve
all identifiers, dates and amounts, mark missing information, and explain
uncertainty. These are model instructions, not a factual verification engine.

## API and deployment references

Documentation checked on 14 October 2026:

- https://trustedtokens.eu/docs/
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management

API: `POST https://api.trustedtokens.eu/v1/chat/completions`, Bearer authentication.
Available model IDs can be checked with authenticated `GET /v1/models` or in your
TrustedTokens account. The model setting is deliberately editable.

## Validation limits

No real API key was supplied, so a live TrustedTokens request and hosted deployment
were not tested. See TEST_RESULTS.txt for the local checks actually performed.


## 4. File upload and camera setup

| Input | Processing |
| --- | --- |
| Type or paste | Enter/edit text directly in the text box |
| PDF | Read text on each page; OCR pages with little or no text |
| Scanned/mixed PDF | Enable full-page OCR to read every page as an image |
| Word `.docx` | Extract paragraphs, table text, headers and footers |
| `.odt`, `.rtf` | Extract document text |
| `.txt`, `.md`, `.csv` | Read UTF-8 text |
| `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff` | German/English OCR |
| Camera | Capture one page, read it, then append further pages if needed |

The text box remains available with every input method. Reading a file replaces
its contents unless **Append to existing text** is selected. Failed imports leave
existing text intact. Check all pages and identifiers before clicking Explain.

Limits: 20 MB per file, 20 PDF/image pages, 25 megapixels per uploaded image,
and 30,000 combined text characters. OCR has a 45-second timeout per page.
Some scans, handwriting, unusual fonts and complex layouts may be misread.
PDF text extraction can miss image content on pages that also contain text;
use full-page OCR in that case. Blank/unreadable pages stop import so pages are
not silently omitted. DOCX/ODT/RTF embedded images are not OCR'd: export such
letters to PDF and enable full-page OCR. Password-protected files are unsupported.

### Install OCR for local use

Python dependencies alone do not install the Tesseract engine. Install it with
both German (`deu`) and English (`eng`) language data:

Windows: follow the Windows installation link in the Tesseract documentation:
https://tesseract-ocr.github.io/tessdoc/Installation.html
Select German and English language data. If the executable is not on PATH, add
this line to `.env` (adjust to your installation):

```dotenv
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
```

Ubuntu / Debian:

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
```

macOS with Homebrew:

```bash
brew install tesseract tesseract-lang
```

Verify the installation (or use the full executable path on Windows):

```bash
tesseract --version
tesseract --list-langs
```

The language list must include `deu` and `eng`. Restart the app after setup.
Typed text, text files and text-based documents can work without OCR; photos
and scanned PDF pages require it.

### Streamlit Cloud

Commit `packages.txt` at the repository root alongside `requirements.txt` and
`app.py`. Streamlit Community Cloud uses it to install the OCR system packages.
Keep your API key in Streamlit Secrets as described above. Do not set a Windows
Tesseract path on the Linux cloud server.

### Camera

Select **Take a picture**, allow browser camera access, capture the page, and
click **Read this picture**. The same editable text box receives the OCR text.
For additional pages, enable **Append this page to existing text**, retake the
photo, and read it. Avoid reading the same capture twice when appending.
Camera access requires a working camera, browser permission, and HTTPS or
localhost. Streamlit Cloud provides HTTPS. If camera access is unavailable,
take a photo with the device camera app and upload the saved image.

### Additional manual checks

- Read a DOCX containing paragraphs, a table, a date, an amount and a reference.
- Read a searchable PDF, then a scanned PDF; compare every page with the source.
- Photograph the sample letter and check German characters and reference digits.
- Append a second photo, then verify both pages appear in the text box.
- Reject an empty file, oversized file and unsupported `.doc` input.
- Clear should remove text/results and reset the upload and camera widgets.

OCR references: https://github.com/madmaze/pytesseract and
https://tesseract-ocr.github.io/tessdoc/Installation.html
System dependencies: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
