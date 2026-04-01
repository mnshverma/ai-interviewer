# AI Interviewer — Agent Context

## Project Identity

- **Name**: MANVER AI Interviewer
- **Type**: Streamlit-based Video Interview Platform
- **Stack**: Python 3.11+ / Streamlit / Kilo AI Gateway API / pypdf / FPDF
- **Deployment**: Streamlit Cloud
- **Brand**: MANVER AI Interviewer — Professional dark theme with blue accents

## Project Overview

A Streamlit-based AI interviewer that:
- Tests camera and microphone permissions
- Captures candidate photo for identity verification
- Collects candidate details (name, email, ID, phone)
- Analyzes resume or job description using Kilo AI Gateway
- Generates technical interview questions
- Conducts live Q&A with proctoring (webcam monitoring)
- Produces AI-generated evaluation reports (PDF)

## Key Architecture Decisions

- **Backend**: Streamlit (Python) — handles all server-side logic
- **State Management**: `st.session_state` — for workflow progression and data
- **AI Integration**: Kilo AI Gateway — for resume analysis, question generation, evaluation
- **PDF Generation**: FPDF — for final evaluation reports
- **No database** — all data in memory (session state)
- **No authentication** — open access interview platform

## Directory Structure

```
.
├── app.py                   # Main Streamlit application (all UI, API calls, state)
├── requirements.txt         # Python dependencies
├── manver-logo.png          # Application logo
├── AGENTS.md                # Agent guidelines (this file)
├── .env                     # Environment variables (API keys) — git-ignored
├── .env.example             # Environment template
├── .gitignore               # Includes .env
└── .agents/                 # AI Agent Configuration
    ├── CONTEXT.md           # Project context (this file)
    ├── CONTEXT.local.md     # Local dev state
    ├── workflows/           # Agent workflow commands
    │   ├── deploy.md        # Streamlit Cloud deployment
    │   └── review.md        # Code review workflow
    ├── skills/              # Specialized agent skills
    │   ├── deploy/SKILL.md   # Deployment skill
    │   └── security-review/SKILL.md
    └── rules/               # Mandatory AI rules
        ├── api-conventions.md
        ├── code-style.md
        ├── error-handling.md
        ├── git-workflow.md
        ├── security.md
        ├── state-management.md
        └── testing.md
```

## Interview State Machine

The app flows through these states (managed in `st.session_state.step`):

```
device_test → photo_capture → setup → analysis → interview → report
```

| State | Description |
|-------|-------------|
| `device_test` | Camera/microphone permission and testing |
| `photo_capture` | Candidate photo capture for identity |
| `setup` | Candidate details form + resume/JD upload |
| `analysis` | AI analysis of resume/JD |
| `interview` | Q&A session with webcam proctoring |
| `report` | Final evaluation report |

## Critical Files Map

| File | Purpose |
|------|---------|
| `app.py` | Main application — all routes, UI, API calls, state management |
| `requirements.txt` | Python dependencies |
| `.env` | API keys (KILO_API_KEY) |

## Key Functions in app.py

| Function | Purpose |
|----------|---------|
| `show_device_test()` | Device permission testing UI |
| `show_photo_capture()` | Photo capture for identity |
| `show_setup()` | Candidate details + resume/JD input |
| `show_analysis()` | AI analysis display |
| `interview_content()` | Q&A with proctoring |
| `show_report()` | Final evaluation |
| `call_ai()` | Kilo API integration |
| `extract_text_from_pdf()` | Resume PDF parsing |
| `create_pdf_report()` | PDF report generation |

## Common Tasks

- **Run locally**: `streamlit run app.py --server.port 8501`
- **Deploy**: See `.agents/skills/deploy/SKILL.md`
- **Add new step**: Add function + update routing in main block
- **Modify API**: Edit `call_ai()` function
- **Change UI**: Edit CSS in `st.markdown()` calls

## Dependencies

| Package | Purpose |
|---------|---------|
| streamlit | Web framework |
| requests | HTTP client for API calls |
| pypdf | PDF text extraction |
| fpdf | PDF report generation |
| python-dotenv | Environment variable loading |

## Rules Summary

Always follow the rules defined in `.agents/rules/`:
- `code-style.md` — Python naming, imports, formatting
- `api-conventions.md` — Kilo API usage patterns
- `error-handling.md` — Graceful degradation, user-friendly errors
- `security.md` — API key protection, no hardcoded secrets
- `project-structure.md` — File organization standards
- `git-workflow.md` — Branch strategy, commit conventions
- `testing.md` — Testing requirements
- `state-management.md` — Streamlit session state patterns