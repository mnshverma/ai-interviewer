---
name: deploy
description: Deploy the Python/Streamlit AI Interviewer to Streamlit Cloud
---

# Deploy Skill (Python)

This skill handles deploying the Python-native AI Interviewer application to Streamlit Cloud or Render.

## Pre-Flight Checks

Before deploying, always run these checks:

### 1. Dependency Check
Ensure all used libraries are in `requirements.txt`:
```bash
# Verify if streamlit, pypdf, requests are present
cat requirements.txt
```

### 2. Local Run Check
Test the app locally to ensure no runtime errors:
```bash
streamlit run app.py
```
Verify the following steps:
- Resume upload works
- Analysis begins correctly
- Interview progress tracks as expected

### 3. Environment Check
Ensure your secret keys are NOT committed to Git.
- Open `.env` and verify it's ignored by `.gitignore`.
- Prepare your `VITE_KILO_API_KEY` for the hosting dashboard.

## Deploy Commands (Streamlit Cloud)

1.  Push your code to **GitHub**.
2.  Connect your repository to [Streamlit Cloud](https://share.streamlit.io/).
3.  In "Advanced Settings" → "Secrets", add:
    ```toml
    VITE_KILO_API_KEY = "your_key_here"
    ```
4.  Deploy!

## Deploy Commands (Render/Heroku)

1.  Use a `Procfile`:
    ```
    web: streamlit run app.py --server.port $PORT
    ```
2.  Add environment variables in the dashboard:
    - `VITE_KILO_API_KEY`

## Post-Deploy Verification

After deployment, verify these features work on the live URL:
1. Page loads without "Connection Error"
2. Resume upload handles PDF files
3. Camera feed appears during "Live Interview"
4. Final report generates and displays correctly

## Rollback Procedure
Revert the last commit on GitHub or redeploy from a previous stable tag/branch on the Streamlit dashboard.
