---
description: How to deploy the Python/Streamlit AI Interviewer
---

# Deploy Workflow (Python)

Follow these steps to deploy your AI Interviewer as a Python-native application.

## Prerequisites

- Python 3.9+
- A GitHub account
- A Kilo.ai API Key (optional for free tier)

## Step 1: Pre-Flight

Ensure all dependencies are in `requirements.txt`:
```bash
pip freeze > requirements.txt
```

## Step 2: Push to Git

1. Initialize git (if not already):
   ```bash
   git init
   ```
2. Check your `.gitignore`:
   ```bash
   # Ensure .env, venv/, and __pycache__/ are listed
   cat .gitignore
   ```
3. Commit and push:
   ```bash
   git add .
   git commit -m "Initial commit for Streamlit version"
   git push origin main
   ```

## Step 3: Streamlit Cloud (Fastest)

1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click "New App" and select your repository.
3. Choose `app.py` as the main file.
4. **Important**: Go to "Advanced Settings" -> "Secrets" and add:
   ```toml
   VITE_KILO_API_KEY = "your_key_here"
   ```
5. Click **Deploy!**

## Step 4: Verification

Once the URL is live:
1. Verify the "Upload Resume" button is interactive.
2. Ensure the "Start Analysis" step works (needs a valid API key or fallback).
3. Test the "Live Interview" video feed.
4. Check if the final report generates and shows properly.
