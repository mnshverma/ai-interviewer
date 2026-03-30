# AI Interviewer — Agent Context

## Project Identity

- **Name**: Manvar AI Interviewer
- **Type**: Resume-Based Live Video Interview Platform
- **Stack**: React 19 + Vite 7 + Vanilla CSS + OpenRouter API
- **Deployment**: Vercel (Static SPA)
- **Brand**: Manvar AI Interviewer — Professional blue & white glassmorphism theme

## Project Overview

An AI-powered interviewer that analyzes resumes and conducts live video interviews with real-time questions, speech recognition (Web Speech API), video recording (WebRTC), and comprehensive AI-generated evaluation reports using OpenRouter (LLaMA 3.1 8B free tier).

## Key Architecture Decisions

- **No backend server** — 100% client-side SPA
- **No state management library** — simple `useState` in `App.jsx`
- **No CSS framework** — custom Vanilla CSS design system in `src/index.css`
- **No external speech services** — browser-native Web Speech API
- **No video upload** — local-only WebRTC MediaRecorder
- **OpenRouter API** — free LLM gateway for resume analysis, question generation, answer evaluation, and final reports

## Directory Structure

```
ai-interviewer/
├── .agents/                        ← AI Agent Configuration (THIS FOLDER)
│   ├── CONTEXT.md                  ← Project context & architecture (this file)
│   ├── CONTEXT.local.md            ← Local dev state, progress, TODO
│   ├── workflows/                  ← Core agent workflow commands
│   │   ├── deploy.md
│   │   ├── fix-issue.md
│   │   └── review.md
│   ├── rules/                      ← Mandatory AI rules for code generation
│   │   ├── api-conventions.md
│   │   ├── code-style.md
│   │   ├── state-management.md
│   │   ├── error-handling.md
│   │   ├── git-workflow.md
│   │   ├── project-structure.md
│   │   ├── security.md
│   │   └── testing.md
│   └── skills/
│       ├── deploy/
│       │   └── SKILL.md
│       └── security-review/
│           └── SKILL.md
├── src/
│   ├── App.jsx                     ← Main orchestrator (state machine)
│   ├── main.jsx                    ← React entry point
│   ├── index.css                   ← Full design system
│   ├── components/
│   │   ├── DataInput.jsx           ← Resume upload & parsing
│   │   ├── ErrorBoundary.jsx       ← Global error boundary
│   │   ├── FinalReport.jsx         ← AI evaluation results
│   │   ├── InterviewHistory.jsx    ← Past interview sessions
│   │   ├── InterviewSettings.jsx   ← Config (API key, type, options)
│   │   ├── ScoreVisualization.jsx  ← Score charts & metrics
│   │   ├── Toast.jsx               ← Notification toasts
│   │   ├── TranscriptPanel.jsx     ← Real-time transcript
│   │   └── VideoInterview.jsx      ← Camera, recording & Q&A flow
│   └── utils/
│       ├── openRouterAPI.js        ← AI/LLM integration layer
│       ├── pdfParser.js            ← PDF.js resume parsing
│       └── speechService.js        ← TTS & STT wrapper
├── public/                         ← Static assets
├── dist/                           ← Production build output
├── .env                            ← API keys (git-ignored)
├── .env.example                    ← Env template
├── package.json
├── vite.config.js
├── vercel.json                     ← Vercel deployment config
└── README.md
```

## Interview State Machine

The app flows through these states (managed in `App.jsx`):

```
setup → analyzing → interviewing → completing → report
```

## Critical Files Map

| File | Purpose |
|------|---------|
| `src/App.jsx` | Main orchestrator — all state, interview flow logic |
| `src/utils/openRouterAPI.js` | ALL AI API calls (resume analysis, questions, evaluation, report) |
| `src/utils/speechService.js` | Text-to-Speech & Speech-to-Text via Web Speech API |
| `src/utils/pdfParser.js` | PDF text extraction via Mozilla pdf.js |
| `src/index.css` | Complete design system (colors, typography, glassmorphism) |
| `src/components/VideoInterview.jsx` | Camera access, MediaRecorder, Q&A interaction |
| `src/components/InterviewSettings.jsx` | API key input, interview type, voice options |
| `src/components/DataInput.jsx` | Resume upload (drag-drop, PDF/TXT) |
| `src/components/FinalReport.jsx` | AI-generated evaluation display |
| `src/components/ScoreVisualization.jsx` | Charts & metrics rendering |
| `src/components/InterviewHistory.jsx` | Past session browser |

## Common Tasks

- **Add a new interview type**: Update `InterviewSettings.jsx` options + `openRouterAPI.js` prompt templates
- **Change AI model**: Edit model ID in `src/utils/openRouterAPI.js`
- **Modify UI theme**: Edit CSS custom properties in `src/index.css`
- **Add a new component**: Create in `src/components/`, import in `App.jsx`
- **Deploy**: `npm run build` → push to Vercel

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^19.2.0 | UI framework |
| react-dom | ^19.2.0 | React DOM renderer |
| pdfjs-dist | ^5.4.530 | PDF text extraction |
| vite | ^7.2.4 | Build tool & dev server |
| eslint | ^9.39.1 | Code linting |

## Rules Summary

Always follow the rules defined in `.agents/rules/`:
- `code-style.md` — React/JSX conventions, naming, CSS patterns
- `api-conventions.md` — OpenRouter API usage, error handling, rate limits
- `error-handling.md` — Graceful degradation, user-friendly errors
- `security.md` — API key protection, data privacy
- `project-structure.md` — File organization standards
- `git-workflow.md` — Branch strategy, commit conventions
- `testing.md` — Testing requirements
- `state-management.md` — Local state & storage patterns
