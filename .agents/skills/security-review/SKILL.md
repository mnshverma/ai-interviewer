---
name: security-review
description: Perform a security review of the AI Interviewer codebase
---

# Security Review Skill

This skill performs a security audit of the AI Interviewer application.

## Review Steps

### 1. API Key Exposure Check

Search for any hardcoded API keys or secrets:
```bash
# Search for potential API key patterns
grep -rn "sk-or-v1" src/ --include="*.js" --include="*.jsx"
grep -rn "api_key\|apiKey\|API_KEY" src/ --include="*.js" --include="*.jsx"
```

Verify:
- [ ] No API keys in source code
- [ ] `.env` is listed in `.gitignore`
- [ ] API key accessed only via `import.meta.env.VITE_OPENROUTER_API_KEY`
- [ ] No `console.log` containing API key values

### 2. Data Flow Audit

Check what data leaves the browser:
- [ ] Only resume text and answers sent to OpenRouter API
- [ ] No analytics or tracking scripts
- [ ] No external CDN requests for user data
- [ ] Video recordings stay local (never uploaded)

Review `src/utils/openRouterAPI.js`:
- [ ] API endpoint is only `https://openrouter.ai/api/v1/chat/completions`
- [ ] No other external API calls
- [ ] Request headers don't leak sensitive info

### 3. Input Validation

Check for injection vulnerabilities:
- [ ] No `eval()` or `new Function()` usage
- [ ] No `innerHTML` with user/AI content (use React JSX)
- [ ] No `dangerouslySetInnerHTML` without sanitization
- [ ] File upload validates type and size

Search for dangerous patterns:
```bash
grep -rn "eval\|innerHTML\|dangerouslySetInnerHTML" src/ --include="*.js" --include="*.jsx"
```

### 4. Browser Permission Review

- [ ] Camera/mic requested only when user initiates interview
- [ ] Permissions not requested on page load
- [ ] Streams properly stopped on cleanup (no orphan streams)
- [ ] MediaRecorder stopped when interview ends

### 5. localStorage Review

- [ ] No unencrypted sensitive data stored
- [ ] API key storage has user consent
- [ ] localStorage reads have try/catch with fallbacks
- [ ] No PII stored without explicit user action

### 6. Dependency Audit

```bash
npm audit
```

Check for known vulnerabilities in:
- `pdfjs-dist`
- `react` / `react-dom`
- Vite and build tooling

## Output

After completing the review, generate a report with:
1. **Critical** — Must fix immediately (key exposure, injection)
2. **Warning** — Should fix soon (missing validation, cleanup)
3. **Info** — Best practice suggestions
