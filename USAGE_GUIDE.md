# 📘 AI Interviewer Usage Guide (Python)

This guide shows you how to use and deploy the Manvar AI Interviewer.

## 🚀 Setting Up Locally

1.  **Check requirements**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **API Key**: Ensure you have `VITE_KILO_API_KEY` in your `.env` file. If not, the app will try to connect anonymously.
3.  **Run Streamlit**:
    ```bash
    streamlit run app.py
    ```

## 🌐 Deployment Options

### 1. Recommended: Streamlit Cloud (Primary Version)
The `app.py` version is the most feature-rich and uses Streamlit's state management.
-   Push your code to **GitHub**.
-   Connect to [Streamlit Cloud](https://share.streamlit.io/).
-   Add `VITE_KILO_API_KEY` to **Advanced Settings -> Secrets**.

### 2. Fallback: Vercel Edition (Static HTML + Python API)
Use this if you prefer Vercel and don't need the specialized Streamlit components.
-   Access it at YOUR-URL/ directly.
-   The UI for this is in `public/index.html` and the API is in `api/index.py`.

## 🎤 Conducting an Interview

1.  **Upload a Resume**: Drag and drop your PDF Resume. AI parses it instantly on the server.
2.  **AI Analysis**: Click "Start Analysis". Review key candidate insights.
3.  **Interview Session**: Respond to technical questions. The webcam check ensure authenticity.
4.  **Final Report**: Once finished, view the automated hiring recommendation and score.

## 💡 Troubleshooting (404 / Runtime Errors)
-   **404 NOT_FOUND**: Checked `vercel.json` rewrites. Ensure you are visiting the root URL.
-   **Package Errors**: If Vercel complains about `vercel-python`, it's not a real package! Use the defaults as updated in `vercel.json`.
