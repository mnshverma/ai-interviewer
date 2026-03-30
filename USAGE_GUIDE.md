# 📘 AI Interviewer Usage Guide (Python)

This guide shows you how to use the new Python-based AI Interviewer.

## 🚀 Setting Up

1.  **Check requirements**:
    ```bash
    pip install streamlit PyPDF2 python-dotenv requests
    ```
2.  **API Key**: Ensure you have `VITE_KILO_API_KEY` in your `.env` file. If not, the app will try to connect anonymously initially.

## 🎤 Conducting an Interview

### Step 1: Uploading a Resume
- Drag and drop your PDF Resume into the browser.
- The app will extract all text automatically.

### Step 2: AI Analysis
- Click "Start Analysis".
- Review the AI-generated context about the candidate. If the context looks right, click "Confirm".

### Step 3: Interview Session
- **Webcam Check**: Your camera feed should appear for the interviewer.
- **Answer Input**: Type your answers in the box.
- **Navigation**: Use "Next Question" to proceed or "Skip" to move to another topic.

### Step 4: Final Report
- Once the last question is answered, the AI will generate a final hiring report including:
  - **Overall Score** (1-10)
  - **Key Strengths**
  - **Areas for Improvement**
  - **Recommendation** (Hire/Maybe/No Hire)

## 💡 Best Practices
- **Resume Format**: Use a clean PDF. Avoid scanned images and very complex layouts.
- **Environment**: Ensure a well-lit area for the camera check.
- **Responses**: Try to be descriptive; the AI evaluates the *content* of your answers.
