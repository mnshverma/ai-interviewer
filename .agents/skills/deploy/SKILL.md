---
name: deploy
description: Deploy the AI Interviewer to Vercel with pre-flight checks
---

# Deploy Skill

This skill handles deploying the AI Interviewer application to Vercel.

## Pre-Flight Checks

Before deploying, always run these checks:

### 1. Lint Check
```bash
npm run lint
```
If there are errors, fix them before proceeding.

### 2. Build Check
```bash
npm run build
```
Verify the build succeeds and `dist/` is created without errors.

### 3. Environment Check
Ensure `VITE_OPENROUTER_API_KEY` is configured in Vercel dashboard:
- Go to Vercel project settings → Environment Variables
- Verify the API key is set for Production, Preview, and Development

## Deploy Commands

### Production Deploy
```bash
vercel --prod
```

### Preview Deploy
```bash
vercel
```

## Post-Deploy Verification

After deployment, verify these features work on the live URL:
1. Page loads without console errors
2. Resume upload (PDF drag-and-drop)
3. API key input accepts key
4. Camera/mic permission prompts appear
5. CSS/fonts render correctly (glassmorphism effects, Inter font)
6. All buttons and dropdowns are interactive

## Rollback Procedure
```bash
vercel ls                # List deployments
vercel rollback          # Roll back to previous
```

## Configuration Reference

The deployment is configured by `vercel.json`:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```
