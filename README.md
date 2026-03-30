# 🐍 Python AI Interviewer (Streamlit Version)

This is the Python-native rewrite of the AI Interviewer. It is faster, has zero CORS issues, and handles PDF parsing more reliably.

## 🚀 Quick Start

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Ensure your .env file** at the root has your API key:
    ```
    VITE_KILO_API_KEY=your_key_here
    ```

3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

## ✨ Features
- **Glassmorphism UI**: High-end styling with custom CSS for a premium feel.
- **Direct AI Gateway**: Communicates directly with Kilo.ai Gateway (No CORS blocks).
- **Native PDF Parsing**: Reliable text extraction using `PyPDF2`.
- **Step-by-Step Flow**: Resume Upload -> AI Analysis -> Questioning -> Automated Report.
- **Camera Check**: Built-in webcam support for the candidate session.
