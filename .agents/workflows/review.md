---
description: How to review code changes in the AI Interviewer project
---

# Code Review Workflow

## Step 1: Understand the Change

1. Check what files were modified:
   ```bash
   git diff --stat
   ```
2. Read the full diff:
   ```bash
   git diff
   ```
3. Understand the intent — what problem does this change solve?

## Step 2: Review Checklist

### Functional Correctness
- [ ] Does the change work as intended?
- [ ] Are edge cases handled (null, empty, error states)?
- [ ] Does the interview state machine remain consistent?
- [ ] Are API calls properly error-handled with user-friendly messages?

### Code Quality (see `.agents/rules/code-style.md`)
- [ ] Follows React functional component patterns
- [ ] Uses `useState` / `useCallback` / `useEffect` correctly
- [ ] No unnecessary re-renders introduced
- [ ] CSS uses existing design tokens (custom properties) from `index.css`
- [ ] No inline styles — all styling in CSS
- [ ] Component files are focused and single-responsibility

### Security (see `.agents/rules/security.md`)
- [ ] No API keys hardcoded or logged
- [ ] No sensitive data exposed in UI or console
- [ ] `.env` variables accessed only via `import.meta.env`

### Error Handling (see `.agents/rules/error-handling.md`)
- [ ] All async operations have try/catch
- [ ] User sees meaningful error messages (not technical stack traces)
- [ ] Graceful degradation (no camera? → show message, continue)

### Performance
- [ ] No large re-renders on every keystroke
- [ ] Blob URLs properly revoked when no longer needed
- [ ] Media streams stopped on cleanup
- [ ] PDF worker loaded lazily

## Step 3: Test the Change

1. Start dev server and manually test the affected feature
2. Test on Chrome (primary) and at least one other browser
3. Check console for warnings or errors
4. Verify mobile responsiveness if UI was changed

## Step 4: Approve or Request Changes

- **Approve**: If all checklist items pass
- **Request Changes**: Comment on specific lines with issues
- **Commit convention**: `feat:`, `fix:`, `refactor:`, `style:`, `docs:`
