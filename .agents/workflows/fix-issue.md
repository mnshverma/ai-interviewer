---
description: How to diagnose and fix issues in the AI Interviewer
---

# Fix Issue Workflow

## Step 1: Reproduce the Issue

1. Run the dev server:
   ```bash
   npm run dev
   ```
2. Open browser DevTools (F12) → Console tab
3. Reproduce the exact steps that cause the issue
4. Note any console errors, warnings, or network failures

## Step 2: Identify the Source

### By Error Location

| Symptom | Likely Source File |
|---------|-------------------|
| Resume upload fails | `src/components/DataInput.jsx` or `src/utils/pdfParser.js` |
| API errors / no AI response | `src/utils/openRouterAPI.js` |
| Camera/mic not working | `src/components/VideoInterview.jsx` |
| Speech not working | `src/utils/speechService.js` |
| UI/styling broken | `src/index.css` or the specific component |
| Interview flow stuck | `src/App.jsx` (state machine logic) |
| Report not generating | `src/components/FinalReport.jsx` + `openRouterAPI.js` |
| Settings not saving | `src/components/InterviewSettings.jsx` |
| Toast errors | `src/components/Toast.jsx` |
| Score display wrong | `src/components/ScoreVisualization.jsx` |

### By Error Type

- **Network/API error** → Check `openRouterAPI.js`, verify API key in `.env`
- **Permission denied** → Browser permission for camera/mic
- **Component crash** → Check `ErrorBoundary.jsx`, look for null/undefined renders
- **State stuck** → Check `App.jsx` state transitions and `interviewState` value

## Step 3: Fix the Issue

1. Read the identified source file
2. Understand the current logic
3. Apply minimal, focused fix
4. Follow rules in `.agents/rules/error-handling.md` and `.agents/rules/code-style.md`

## Step 4: Verify the Fix

1. Test the specific scenario that was broken
2. Test adjacent features (ensure no regression)
3. Run lint:
   ```bash
   npm run lint
   ```
4. Build check:
   ```bash
   npm run build
   ```

## Step 5: Commit

```bash
git add .
git commit -m "fix: <brief description of what was fixed>"
```
