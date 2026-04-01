# Project Structure — AI Interviewer

## Standard Structure

```
.
├── app.py                   # Main Streamlit application (ALL code in one file)
├── requirements.txt         # Python dependencies
├── manver-logo.png          # Application logo (base64 encoded in app.py)
├── AGENTS.md                # Agent guidelines for developers
├── .env                     # Secrets (git-ignored)
├── .env.example             # Environment template (committed)
├── .gitignore               # Includes .env, .env.local, etc.
└── .agents/                 # AI Agent Configuration
    ├── CONTEXT.md           # Project context (architecture, file map)
    ├── CONTEXT.local.md     # Local state, progress, TODO
    ├── workflows/           # Agent workflow commands
    │   ├── deploy.md        # Streamlit Cloud deployment
    │   └── review.md        # Code review workflow
    └── rules/               # Mandatory AI rules
        ├── api-conventions.md
        ├── code-style.md
        ├── error-handling.md
        ├── git-workflow.md
        ├── security.md
        ├── state-management.md
        └── testing.md
```

## Rules for This Project

### Single File Architecture
- **ALL application code lives in `app.py`** — no separate modules or packages
- Functions are defined in the order: helpers → state init → page functions → main routing
- CSS is defined via `st.markdown()` with `<style>` blocks

### Adding New Features
1. Add helper functions near the top of `app.py` (after imports, before state init)
2. Add page functions after the helper functions
3. Update the routing logic at the bottom of the file
4. Add CSS styles to the `<style>` block in the markup section

### Adding New State Variables
1. Initialize in the state initialization block (after `st.markdown()`)
2. Use descriptive snake_case names
3. Document in AGENTS.md if it's a critical state variable

### Environment Variables
- **NEVER hardcode API keys** — use `os.getenv()` or `.env` file
- Required: `VITE_KILO_API_KEY` or `KILO_API_KEY`
- Store in `.env` (git-ignored)

## Files That Should NOT Be Modified
- `requirements.txt` — only update to add new dependencies
- `.gitignore` — managed by project rules

## Files That Should NOT Be Created
- No separate `.py` modules — all code in `app.py`
- No `tests/` directory — manual testing via Streamlit
- No `utils/` directory — helper functions in main file