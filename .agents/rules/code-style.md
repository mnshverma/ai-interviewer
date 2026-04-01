# Code Style — AI Interviewer

## Language & Framework
- **Python 3.11+**
- **Streamlit** for UI
- **Kilo AI Gateway** for AI integration

## Python Conventions

### Imports
Order imports strictly:
1. Standard library (`os`, `datetime`, `base64`, `json`, `time`)
2. Third-party (`streamlit`, `requests`, `pypdf`, `dotenv`, `fpdf`)
3. No local imports (all code in single `app.py` file)

```python
import os
import json
import time
from datetime import datetime
import base64

import streamlit as st
import requests
from pypdf import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF
```

### Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Functions | snake_case | `get_api_key()`, `show_device_test()` |
| Classes | PascalCase | `InterviewSession` |
| Constants | UPPER_SNAKE_CASE | `KILO_API_URL`, `DEFAULT_MODEL` |
| Session State Keys | snake_case | `device_test_step`, `persistent_photo` |
| File | lowercase | `app.py` |

### Functions
- Use type hints for parameters and return types (preferred, not required)
- Use descriptive names that indicate purpose
- Keep functions focused (single responsibility)

```python
def call_ai(messages: list, model: str = DEFAULT_MODEL, retries: int = 3) -> str | None:
    """Call Kilo AI Gateway API with retry logic."""
    ...
```

### Error Handling
- Always wrap API calls and file operations in try/except
- Return sensible defaults on failure
- Show user-friendly messages via `st.error()`

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

## Streamlit-Specific Rules

### Session State
- Initialize all session state variables at the top (after CSS definition)
- Use descriptive snake_case names
- Document critical state variables in AGENTS.md

```python
if 'step' not in st.session_state:
    st.session_state.step = 'device_test'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}
```

### UI Components
- Use `st.markdown()` with `unsafe_allow_html=True` for CSS styling only
- Never pass user input directly to `unsafe_allow_html=True`
- Use Streamlit's built-in components: `st.button()`, `st.text_input()`, `st.camera_input()`, etc.

### Page Functions
- One function per page/stage (e.g., `show_device_test()`, `show_setup()`)
- Use `st.session_state.step` for routing

```python
step = st.session_state.get('step', 'device_test')

if step == 'device_test':
    show_device_test()
elif step == 'photo_capture':
    show_photo_capture()
elif step == 'setup':
    show_setup()
```

## Formatting
- Max line length: 100 characters
- Use f-strings for string interpolation
- 2 spaces for indentation (no tabs)
- Blank line between function definitions

## Code Quality
- No debug prints in production (remove before commit)
- Remove `st.write()` debug statements
- Test Python syntax before commit: `python -m py_compile app.py`