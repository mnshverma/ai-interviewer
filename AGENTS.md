# AI Interviewer - Agent Guidelines

## Project Overview

This is a Streamlit-based AI Interviewer application that conducts video interviews with candidates. The app uses the Kilo AI Gateway API for AI-powered evaluation.

**Tech Stack:**

- Streamlit (web framework)
- Python 3.11+
- Kilo AI Gateway API (chat/completions, models)
- pypdf (PDF parsing)
- FPDF (PDF report generation)

---

## Build & Run Commands

### Run the Application

```bash
streamlit run app.py --server.port 8501
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Lint & Type Check (if configured)

```bash
# Python syntax check
python -m py_compile app.py

# Format with black (if installed)
black app.py --line-length 100
```

---

## Code Style Guidelines

### Imports

- Standard library imports first, then third-party, then local
- Group by: `os`, `datetime`, `base64` (stdlib) → `streamlit`, `requests`, `pypdf` (third-party) → project modules
- Example:

```python
import streamlit as st
import requests
from pypdf import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF
```

### Naming Conventions

- **Functions**: `snake_case` - e.g., `get_api_key()`, `show_device_test()`
- **Classes**: `PascalCase` - e.g., `InterviewSession`
- **Constants**: `UPPER_SNAKE_CASE` - e.g., `KILO_API_URL`, `DEFAULT_MODEL`
- **Session State Keys**: `snake_case` with descriptive names - e.g., `device_test_step`, `persistent_photo`

### Formatting

- Max line length: 100 characters
- Use f-strings for string interpolation
- Use `st.markdown(..., unsafe_allow_html=True)` for HTML content
- CSS in `<style>` blocks within markdown, indented properly

### Error Handling

- Use try/except blocks for API calls and file operations
- Return sensible defaults on failure (e.g., fallback model list)
- Show user-friendly error messages via `st.error()`
- Example:

```python
def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""
```

### Type Hints

- Optional but preferred for function signatures
- Example:

```python
def call_ai(messages: list, model: str = DEFAULT_MODEL, retries: int = 3) -> str | None:
    ...
```

---

## Directory Structure

```
.
├── app.py              # Main application (all routes, UI, API calls)
├── requirements.txt    # Python dependencies
├── manver-logo.png     # Application logo
├── .env               # Environment variables (API keys)
└── .env.example       # Environment template
```

---

## Key Patterns

### Streamlit Session State

Always initialize session state variables before use:

```python
if 'step' not in st.session_state:
    st.session_state.step = 'device_test'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}
```

### API Calls

- Use `requests` library with timeout
- Include proper headers (Content-Type, Authorization)
- Handle non-200 responses gracefully

### CSS Styling

- Use CSS variables for colors (`--accent-blue`, `--bg-primary`)
- Target Streamlit components via data-testid attributes
- Keep styles scoped to avoid conflicts

### Page Routing

Use `st.session_state.step` to manage workflow:

```python
step = st.session_state.get('step', 'device_test')

if step == 'device_test':
    show_device_test()
elif step == 'photo_capture':
    show_photo_capture()
# ... etc
```

---

## Workflow Steps

1. **device_test** - Camera/microphone permission and testing
2. **photo_capture** - Candidate photo capture for identity
3. **eye_calibration** - Gaze tracking calibration for proctoring
4. **setup** - Candidate details form (name, email, ID, phone)
5. **analysis** - AI analysis of resume/JD
6. **interview** - Q&A session with proctoring
7. **report** - Final evaluation report

---

## Important Notes

- Never hardcode API keys - use `os.getenv()` / `.env` file
- The Kilo API endpoint is `https://api.kilo.ai/api/gateway`
- Chat completions: POST to `/chat/completions`
- List models: GET to `/models`
- Always test Python syntax before committing: `python -m py_compile app.py`
