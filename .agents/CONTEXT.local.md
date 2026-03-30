# Local Configuration — AI Interviewer

## Developer Context

- **Primary Developer**: Manish Verma
- **Brand Name**: Manvar AI Interviewer
- **Working Directory**: `c:\automation\ai-interviewer`
- **Node Version**: 18+ recommended
- **Package Manager**: npm
- **Last Updated**: 2026-03-30

## Local Environment

### Dev Commands

```bash
npm run dev          # Start Vite dev server → http://localhost:5173
npm run build        # Production build → dist/
npm run preview      # Preview production build locally
npm run lint         # Run ESLint
```

### Environment Variables

```
VITE_OPENROUTER_API_KEY=sk-or-v1-...   # Required for AI features
```

- `.env` file is git-ignored
- `.env.example` has the template

## Current State & Progress

### ✅ Completed Features
- Resume upload (PDF + TXT) with pdf.js parsing
- Interview configuration (API key, interview type, voice settings)
- Live video interview with webcam + recording
- AI question generation based on resume analysis
- Speech-to-text answer capture
- Text-to-speech AI voice for questions
- Real-time transcript with timestamps
- Comprehensive AI evaluation report
- Score visualization with charts
- Interview history tracking
- Modern glassmorphism UI with professional blue/white theme
- Toast notification system
- Error boundary for crash recovery
- Vercel deployment configuration
- Free model selector (OpenRouter free tier models)

### 🔄 In Progress
- (Check `git log --oneline -10` for latest work)

### 📋 TODO / Known Issues
- DOCX support is limited
- Safari speech recognition has partial support
- Rate limiting on free OpenRouter tier needs monitoring
- No offline capability yet (Service Worker planned)
- Multi-language support (i18n) planned
- Custom question banks planned
- Code editor for live coding challenges planned

## Design System Quick Reference

- **Primary Color**: Professional Blue (#2563eb range)
- **Background**: White/Light with glassmorphism effects
- **Font**: System font stack (Inter if available)
- **Border Radius**: Rounded corners (8-16px)
- **Shadows**: Subtle elevation system
- **Animations**: Smooth transitions, micro-interactions
- **Theme**: Blue & white professional, glassmorphism aesthetic

## Debugging Tips

1. **API not working?** → Check `.env` key, try different free model in `openRouterAPI.js`
2. **Camera not starting?** → Check browser permissions, ensure no other app uses camera
3. **Speech not recognized?** → Chrome recommended, check microphone in OS settings
4. **Build fails?** → Run `npm install` first, check Node version ≥18
5. **Styles broken?** → Check `src/index.css`, all design tokens are CSS custom properties
