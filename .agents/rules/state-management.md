# State Management & Storage — AI Interviewer

## Overview
This app has **NO backend database**. All state is either:
1. **React state** (in-memory, lost on refresh)
2. **localStorage** (persisted in browser)
3. **Environment variables** (build-time config)

## React State (App.jsx)

All interview state is centralized in `App.jsx`:

```javascript
// Core interview state
const [resumeData, setResumeData] = useState(null);          // Parsed resume text
const [interviewConfig, setInterviewConfig] = useState(null); // API key, type, options
const [interviewState, setInterviewState] = useState("setup"); // State machine
const [resumeAnalysis, setResumeAnalysis] = useState("");      // AI resume analysis
const [questions, setQuestions] = useState([]);                 // Generated questions
const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
const [transcript, setTranscript] = useState([]);              // Q&A transcript
const [isAISpeaking, setIsAISpeaking] = useState(false);       // TTS active flag
const [isListening, setIsListening] = useState(false);         // STT active flag
const [finalReport, setFinalReport] = useState(null);          // AI evaluation
```

### State Machine Transitions
```
setup        → analyzing     (on "Start Interview" click)
analyzing    → interviewing  (after questions generated)
interviewing → completing    (after last question answered)
completing   → report        (after final report generated)
report       → setup         (on "New Interview" click)
```

### Rules
- **Never** create duplicate state in child components for data that comes from App.jsx
- **Never** use `useContext` or Redux — this app is simple enough for prop drilling
- **Always** use functional updates when new state depends on previous: `setState(prev => ...)`

## localStorage Usage

### What Gets Persisted
- **Interview History**: Past interview sessions (scores, dates, types)
- **API Key**: Optionally saved for convenience (encrypted in future)
- **User Preferences**: Voice on/off, recording on/off

### localStorage Keys
| Key | Type | Purpose |
|-----|------|---------|
| `interviewHistory` | JSON array | Past interview sessions |
| `openrouter_api_key` | string | Saved API key |
| `interview_preferences` | JSON object | User settings |

### localStorage Rules
- Always wrap in try/catch (storage may be full or disabled)
- Always JSON.parse with fallback: `JSON.parse(value) ?? defaultValue`
- Never store sensitive data without encryption warning to user
- Clean up old entries if history grows too large (max 50 sessions)

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `VITE_OPENROUTER_API_KEY` | Yes | OpenRouter API access |

- Access via `import.meta.env.VITE_OPENROUTER_API_KEY`
- Must be prefixed with `VITE_` for Vite to expose to client
- Set in `.env` file (git-ignored) or Vercel dashboard
