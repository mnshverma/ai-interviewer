# Testing — AI Interviewer

## Current Testing Approach
This project currently uses **manual testing** as the primary QA method. Automated tests are a future enhancement.

## Manual Testing Checklist

### Resume Upload
- [ ] PDF upload works (drag-and-drop + click)
- [ ] TXT upload works
- [ ] Large files (>1MB) handled gracefully
- [ ] Invalid files show error message
- [ ] Resume text preview shows correctly

### Interview Settings
- [ ] API key input accepts and validates key format
- [ ] Interview type dropdown works (Technical, Behavioral, Mixed, Leadership)
- [ ] Voice toggle works
- [ ] Recording toggle works
- [ ] "Start Interview" disabled until resume + API key provided

### Video Interview
- [ ] Camera preview starts correctly
- [ ] Recording indicator shows when recording
- [ ] AI question displays on screen
- [ ] TTS speaks the question (when voice enabled)
- [ ] "Start Recording Answer" begins STT
- [ ] "Stop & Submit" captures the answer
- [ ] Next question loads after submission
- [ ] Progress indicator updates

### AI Integration
- [ ] Resume analysis returns meaningful result
- [ ] Questions are relevant to the resume
- [ ] Answer evaluation provides feedback
- [ ] Final report is comprehensive and structured
- [ ] Fallback models work when primary fails

### Report & History
- [ ] Final report displays with scores
- [ ] Score visualization renders correctly
- [ ] Download transcript works
- [ ] Download recording works (when recorded)
- [ ] Interview saved to history
- [ ] History panel shows past interviews

### Cross-Browser
- [ ] Chrome (primary — all features)
- [ ] Edge (all features)
- [ ] Firefox (speech recognition may differ)
- [ ] Safari (limited speech recognition)

### Responsive Design
- [ ] Desktop (1920px+)
- [ ] Laptop (1366px)
- [ ] Tablet (768px)
- [ ] Mobile (375px)

## Future: Automated Testing

### Planned Stack
```
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
```

### Unit Test Targets
- `src/utils/openRouterAPI.js` — Mock API responses, test parsing
- `src/utils/pdfParser.js` — Test text extraction
- `src/utils/speechService.js` — Test service initialization

### Component Test Targets
- `DataInput.jsx` — File selection, validation
- `InterviewSettings.jsx` — Form validation, state
- `FinalReport.jsx` — Report rendering with various data shapes

### Test File Convention
```
src/
├── utils/
│   ├── openRouterAPI.js
│   └── __tests__/
│       └── openRouterAPI.test.js
├── components/
│   ├── DataInput.jsx
│   └── __tests__/
│       └── DataInput.test.jsx
```
