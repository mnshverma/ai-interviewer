---
name: security-review
description: Perform a security review of the AI Interviewer Python codebase
---

# Security Review Skill (Python)

This skill performs a security audit of the Python-native AI Interviewer application based on Streamlit.

## Review Steps

### 1. API Key Exposure Check

Search for any hardcoded API keys or secrets in `app.py`:
```bash
# Search for potential API key patterns
grep -rn "ki-*" app.py
grep -rn "api_key\|apiKey\|API_KEY" app.py
```

Verify:
- [ ] No API keys in source code (must use `os.getenv` or `st.secrets`)
- [ ] `.env` is listed in `.gitignore`
- [ ] API key is not logged to the Streamlit UI using `st.write` or `st.code`
- [ ] Omit `VITE_KILO_API_KEY` from public logs

### 2. Streamlit Security (XSS/CSRF)

Check how user data is handled in the UI:
- [ ] Use `st.markdown(..., unsafe_allow_html=True)` only for styling
- [ ] No direct user input passed to `unsafe_allow_html=True`
- [ ] Resume text and answer text are sanitized by Streamlit (default)
- [ ] PDF parsing happens on the server side (no browser data leaks)

### 3. Data Flow Audit

Check what data leaves the server (Python process):
- [ ] Only resume text and session transcripts sent to Kilo AI Gateway
- [ ] No external 3rd-party tracking scripts
- [ ] No tracking pixels or analytics in custom CSS markdown
- [ ] Webcam stream stays local to the browser components (standard `st.camera_input`)

### 4. Dependency Audit (Python)

Use `pip-audit` or similar tools:
```bash
# Verify if any library has known vulnerabilities
pip-audit -r requirements.txt
```

Check specifically:
- `pypdf` (ensure version is up to date)
- `streamlit` (check for known security advisories)
- `requests` (verify SSL verification is NOT disabled)

### 5. Input Validation

Check for injection vulnerabilities in Python:
- [ ] No usage of `eval()` or `exec()` on user strings
- [ ] Prompt construction uses f-strings with sanitized context (no prompt injection potential)
- [ ] File upload validates PDF headers before process

## Output

After completing the review, generate a report with:
1. **Critical** — Must fix immediately (hardcoded keys, exec() usage)
2. **Warning** — Should fix soon (missing validation in PDF parser)
3. **Info** — Best practice suggestions (XSS hardening in custom CSS)
