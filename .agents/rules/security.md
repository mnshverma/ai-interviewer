# Security — AI Interviewer

## API Key Protection

### DO
- Store API key in `.env` file (git-ignored)
- Access via `os.getenv("VITE_KILO_API_KEY")` or `os.getenv("KILO_API_KEY")`
- List `.env` in `.gitignore`

### DON'T
- Never hardcode API keys in source code
- Never `st.write()` or `st.code()` API keys
- Never include API keys in error messages shown to users
- Never commit `.env` to git

## Data Privacy

### Server-Side Processing
- All processing happens on the Streamlit server (Python)
- Resumes are parsed server-side via pypdf
- Data stays in memory (session state)

### What Gets Sent Externally
- **Resume text** → Kilo AI Gateway (for analysis & question generation)
- **User answers** → Kilo AI Gateway (for evaluation)
- **Nothing else** — no analytics, no tracking, no telemetry

## Browser Permissions (Streamlit Components)

### Required Permissions
| Permission | Required For | Fallback if Denied |
|------------|-------------|-------------------|
| Camera | Video proctoring | st.camera_input shows error |
| Microphone | Voice input | st.audio_input shows error |

### Permission Handling
- Streamlit handles permission prompts automatically via browser
- Use `st.camera_input()` and `st.audio_input()` for permission requests
- Handle denial gracefully with informative messages

## Content Security
- No `eval()` or `exec()` usage
- No user input passed to `st.markdown(..., unsafe_allow_html=True)` — only static CSS
- User input rendered via Streamlit's default sanitization

## HTTPS
- Production deployment on Streamlit Cloud uses HTTPS by default
- Camera/Microphone APIs require HTTPS (except localhost)

## Input Validation
- Validate file uploads before processing
- Check PDF headers before parsing
- Sanitize any user-provided text before sending to AI

## SSL/TLS
- Always keep SSL verification enabled (never use `verify=False` in requests)
- Default `requests` library behavior is secure