# 🏗️ AI Interviewer Architecture (Python)

The Manver AI Interviewer is now a **Python 3.x** application built with **Streamlit**. It uses a single-process server model for real-time AI interviewing.

## 🧱 Component Overview

### 1. The Frontend (Streamlit)
- **UI Engine**: Streams state-based HTML from Python to the browser.
- **Glassmorphism Layer**: Custom CSS injected via `st.markdown` to provide a premium, modern aesthetic.
- **Media Handling**: Uses `st.camera_input` for real-time candidate verification.

### 2. The AI Gateway (Requests)
- **Endpoint**: Direct HTTPS calls to `https://api.kilo.ai/api/gateway/chat/completions`.
- **Logic**: All AI calls are centralized in `app.py`. It uses a retry-mechanism and model fallback.
- **Authentication**: Supports both Kilo API Keys and Anonymous free-tier sessions.

### 3. PDF Parsing (PyPDF2)
- **Engine**: Pure Python parsing on the server side.
- **Reliability**: No longer relies on browser-side workers, solving most text extraction issues.

### 4. State Machine
We use Streamlit's `session_state` to track the interview progress:
- `setup` -> `analysis` -> `interview` -> `report`

## 🔄 Data Flow
1. User uploads a PDF Resume.
2. Python extracts text and sends it to Kilo AI for analysis.
3. Analysis is used to generate specific interview questions.
4. Live interview session begins (Camera + Text Input).
5. Responses are analyzed and a final hiring report is generated.
