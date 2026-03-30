# Security — AI Interviewer

## API Key Protection

### DO
- Store API key in `.env` file (git-ignored)
- Access via `import.meta.env.VITE_OPENROUTER_API_KEY`
- Allow user to input key via UI (InterviewSettings.jsx)
- Mask key display in UI (show only last 4 characters)

### DON'T
- Never hardcode API keys in source code
- Never `console.log` API keys
- Never include API keys in error messages shown to users
- Never commit `.env` to git
- Never send API key to any endpoint other than OpenRouter

## Data Privacy

### Client-Side Only
- All processing happens in the browser
- Resumes are parsed locally via pdf.js
- Video recordings stay local (no upload)
- Transcripts are stored only in React state (lost on refresh) or localStorage

### What Gets Sent Externally
- **Resume text** → OpenRouter API (for analysis & question generation)
- **User answers** → OpenRouter API (for evaluation)
- **Nothing else** — no analytics, no tracking, no telemetry

### localStorage Security
- API keys stored in localStorage are accessible to any script on the same origin
- Warn users: "Your API key is stored in your browser"
- Never store tokens without user consent

## Browser Permissions

### Required Permissions
| Permission | Required For | Fallback if Denied |
|------------|-------------|-------------------|
| Camera | Video interview | Continue without video |
| Microphone | Voice answers | Text input fallback |

### Permission Handling
- Request permissions only when needed (not on page load)
- Explain to user WHY the permission is needed before requesting
- Handle denial gracefully with fallback options
- Never repeatedly prompt after user denies

## Content Security
- No `eval()` or `new Function()` usage
- No `innerHTML` with user content — use React's JSX rendering
- Sanitize any AI-generated content before rendering
- Use `dangerouslySetInnerHTML` only when absolutely necessary (prefer React elements)

## HTTPS
- Production deployment on Vercel uses HTTPS by default
- Camera/Microphone APIs require HTTPS (except localhost)
- All API calls to OpenRouter use HTTPS
