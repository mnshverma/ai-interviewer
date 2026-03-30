---
description: How to deploy the AI Interviewer application to Vercel
---

# Deploy AI Interviewer

## Pre-Deployment Checklist

1. **Ensure build succeeds locally:**
   ```bash
   npm run build
   ```
   Verify no errors and `dist/` folder is created.

2. **Verify environment variables:**
   - `VITE_OPENROUTER_API_KEY` must be set in Vercel dashboard (not committed to git)
   - Check `.env.example` for all required variables

3. **Run lint:**
   ```bash
   npm run lint
   ```
   Fix any warnings/errors before deploying.

## Deployment Steps

### Option A: Vercel CLI

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Option B: Git Push (auto-deploy)

```bash
git add .
git commit -m "feat: <description>"
git push origin main
```
Vercel auto-deploys on push to `main` branch.

## Post-Deployment Verification

1. Open the deployed URL
2. Verify resume upload works (PDF + TXT)
3. Test API key input and interview start flow
4. Check camera/microphone permissions prompt
5. Verify all CSS/fonts load correctly

## Rollback

```bash
# List recent deployments
vercel ls

# Roll back to previous deployment
vercel rollback
```

## Vercel Configuration

The `vercel.json` at project root handles:
- Build command: `npm run build`
- Output directory: `dist`
- SPA rewrites: all routes → `/index.html`
- Framework: Vite
