# State Management & Storage — AI Interviewer

## Overview
This app has **NO backend database**. All state is managed via:
1. **Streamlit Session State** (in-memory, lost on refresh)
2. **Environment variables** (API keys, configuration)

## Streamlit Session State

All application state is stored in `st.session_state`:

### Core State Variables
```python
# Workflow control
st.session_state.step = 'device_test'  # Current page/stage

# User data
st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}
st.session_state.persistent_photo = None  # Captured photo
st.session_state.interview_time = None      # Interview timestamp

# Interview data
st.session_state.analysis = ""       # AI resume/JD analysis
st.session_state.questions = []      # Generated interview questions
st.session_state.answers = []         # User's answers
st.session_state.current_q = 0       # Current question index

# Verification flags
st.session_state.device_test_done = False
st.session_state.device_permissions_granted = False
st.session_state.mic_verified = False
st.session_state.photo_verified = False

# API data
st.session_state.available_models = []  # Fetched from Kilo API
```

### State Machine Transitions
```
device_test → photo_capture → setup → analysis → interview → report
```

### Initialization Pattern
Always initialize all session state variables in one place (after CSS, before page functions):

```python
if 'step' not in st.session_state: 
    st.session_state.step = 'device_test'

if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}

# ... continue for all state variables
```

### Rules
- **Always** initialize before use to avoid KeyError
- **Never** rely on default values — always set in initialization block
- **Use** descriptive snake_case names
- **Preserve** critical flags when transitioning between steps

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `VITE_KILO_API_KEY` | No | Kilo API key for higher rate limits |
| `KILO_API_KEY` | No | Alternative API key name |

- Access via `os.getenv("VITE_KILO_API_KEY")` or `os.getenv("KILO_API_KEY")`
- Store in `.env` file (git-ignored)
- Fall back to anonymous mode if not provided

## No localStorage or Database
- Streamlit doesn't have access to browser localStorage
- All data is in-memory only
- "New Interview" button clears all session state