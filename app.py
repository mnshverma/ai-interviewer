import streamlit as st
import os
import requests
import json
from pypdf import PdfReader
from dotenv import load_dotenv
import time
from fpdf import FPDF
from datetime import datetime
import base64
from eye_tracking import EyeTracker

load_dotenv()
LOGO_PATH = "manver-logo.png"
with open(LOGO_PATH, "rb") as f: 
    LOGO_BASE64 = base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="MANVER AI INTERVIEWER",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add skip link for accessibility
st.markdown("""
    <a href="#main-content" class="skip-link">Skip to main content</a>
""", unsafe_allow_html=True)

KILO_API_URL = "https://api.kilo.ai/api/gateway"
DEFAULT_MODEL = "kilo-auto/free"

def get_free_models():
    try:
        res = requests.get(f"{KILO_API_URL}/models", timeout=10)
        if res.status_code == 200:
            data = res.json()
            models = []
            for m in data.get("data", []):
                model_id = m.get("id", "")
                pricing = m.get("pricing", {})
                is_free = float(pricing.get("prompt", 1)) == 0 and float(pricing.get("completion", 1)) == 0
                if is_free or "/free" in model_id.lower() or "free" in m.get("owned_by", "").lower():
                    models.append(model_id)
            if not models:
                models = ["kilo-auto/free", "minimax/minimax-m2.5:free"]
            return models
    except:
        pass
    return ["kilo-auto/free", "minimax/minimax-m2.5:free"]

def safe_api_call(func, *args, **kwargs):
    """Wrapper for API calls with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"⚠️ Service temporarily unavailable: {str(e)}")
        return None

def show_loading_overlay(message="Loading...", spinner=True):
    """Show a full-screen loading overlay that prevents interaction"""
    overlay_html = f'''
    <div id="loading-overlay" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(2px);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
    ">
        <div style="text-align: center;">
            {"<div style='font-size: 3rem; margin-bottom: 1rem;'>⏳</div>" if spinner else ""}
            <h3 style="color: white; margin-bottom: 0.5rem;">{message}</h3>
            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;">Please wait...</p>
            {"<div style='width: 40px; height: 40px; border: 3px solid rgba(255, 255, 255, 0.3); border-radius: 50%; border-top-color: white; animation: spin 1s linear infinite; margin: 0 auto;'></div>" if spinner else ""}
        </div>
    </div>

    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    /* Disable scrolling when overlay is active */
    body {{
        overflow: hidden !important;
    }}
    </style>
    '''
    st.markdown(overlay_html, unsafe_allow_html=True)

def hide_loading_overlay():
    """Hide the loading overlay"""
    st.markdown("""
    <script>
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    document.body.style.overflow = 'auto';
    </script>
    """, unsafe_allow_html=True)

if 'available_models' not in st.session_state:
    st.session_state.available_models = safe_api_call(get_free_models) or ["kilo-auto/free"]

if 'device_test_done' not in st.session_state:
    st.session_state.device_test_done = False
if 'device_permissions_granted' not in st.session_state:
    st.session_state.device_permissions_granted = False
if 'device_test_step' not in st.session_state:
    st.session_state.device_test_step = 0

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2332;
        --bg-card-hover: #232d3f;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-yellow: #f59e0b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: rgba(255, 255, 255, 0.08);
    }

    * {
        font-family: 'Inter', sans-serif !important;
    }

    /* Accessibility & Keyboard Navigation */
    button, input, textarea, select {
        transition: all 0.2s ease !important;
    }

    button:focus, input:focus, textarea:focus, select:focus {
        outline: 2px solid #3b82f6 !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Skip link for screen readers */
    .skip-link {
        position: absolute;
        top: -40px;
        left: 6px;
        background: #3b82f6;
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
    }

    .skip-link:focus {
        top: 6px;
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
        :root {
            --bg-primary: #000000;
            --bg-secondary: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --border-color: #ffffff;
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    .stApp {
        background: var(--bg-primary);
        background-image: 
            radial-gradient(ellipse at 20% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
        min-height: 100vh;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        [data-testid="column"] {
            min-width: auto !important;
            width: 100% !important;
        }

        .question-card {
            font-size: 1.2rem !important;
        }

        .card {
            padding: 1rem !important;
        }
    }

    @media (max-width: 480px) {
        .stApp {
            font-size: 14px;
        }

        h1 {
            font-size: 1.75rem !important;
        }

        h3 {
            font-size: 1.25rem !important;
        }

        .question-card {
            font-size: 1.1rem !important;
            padding: 1rem !important;
        }

        .info-badge {
            font-size: 0.65rem !important;
            padding: 0.2rem 0.6rem !important;
        }
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="stHeader"], [data-testid="stFooter"], 
    [data-testid="stMainBlockMenu"], #MainMenu, footer, header {
        display: none !important;
        visibility: hidden !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    h1 {
        font-size: 2rem !important;
        letter-spacing: -0.02em;
    }

    h2 {
        font-size: 1.35rem !important;
        color: var(--accent-cyan) !important;
        -webkit-text-fill-color: var(--accent-cyan);
    }

    h3 {
        font-size: 1.1rem !important;
        color: var(--text-secondary) !important;
        -webkit-text-fill-color: var(--text-secondary);
    }

    .page-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }

    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }

    .card-simple {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }

    .card-icon {
        font-size: 1.5rem;
    }

    .card-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 1.1rem;
    }

    .page-title {
        text-align: center;
        margin-bottom: 2rem;
    }

    .page-title h1 {
        font-size: 2.25rem !important;
        margin-bottom: 0.5rem;
    }

    .page-title p {
        color: var(--text-secondary);
        font-size: 1rem;
    }

    .step-indicator {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }

    .step-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: var(--border-color);
    }

    .step-dot.active {
        background: var(--accent-blue);
    }

    .step-dot.completed {
        background: var(--accent-green);
    }

    .stFileUploader {
        background: rgba(0, 0, 0, 0.2);
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: var(--accent-blue) !important;
        background: rgba(59, 130, 246, 0.05) !important;
    }

    .stFileUploader [data-testid="stFileUploadDropzone"] {
        background: transparent !important;
        border: none !important;
    }

    .stFileUploader [data-testid="stFileUploadDropzone"] button {
        background: var(--accent-blue) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
    }

    .stFileUploader [data-testid="stFileUploadDropzone"] button:hover {
        background: #2563eb !important;
    }

    .upload-zone {
        background: rgba(0, 0, 0, 0.25);
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .upload-zone:hover {
        border-color: var(--accent-blue);
        background: rgba(59, 130, 246, 0.05);
    }

    .upload-zone.dragover {
        border-color: var(--accent-cyan);
        background: rgba(6, 182, 212, 0.1);
    }

    .upload-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .upload-text {
        color: var(--text-primary);
        font-weight: 500;
        margin-bottom: 0.25rem;
    }

    .upload-hint {
        color: var(--text-muted);
        font-size: 0.85rem;
    }

    .file-selected {
        background: rgba(16, 185, 129, 0.1);
        border: 2px solid var(--accent-green);
        border-radius: 12px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .file-selected-icon {
        font-size: 1.5rem;
    }

    .file-selected-info {
        flex: 1;
    }

    .file-selected-name {
        color: var(--text-primary);
        font-weight: 500;
    }

    .file-selected-size {
        color: var(--text-muted);
        font-size: 0.85rem;
    }

    .file-selected .remove-btn {
        color: var(--accent-red);
        cursor: pointer;
        padding: 0.25rem;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    .stSelectbox > div > div > div {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }

    .stRadio > div {
        display: flex;
        gap: 0.5rem;
    }

    .stRadio > div > label {
        background: rgba(0, 0, 0, 0.3);
        padding: 0.6rem 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        cursor: pointer;
        color: var(--text-secondary);
    }

    .stRadio > div > label:has(input:checked) {
        background: rgba(59, 130, 246, 0.2);
        border-color: var(--accent-blue);
        color: var(--accent-blue);
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
    }

    .stCameraInput video {
        border-radius: 12px !important;
        max-height: 200px !important;
    }

    .stAudioInput > div {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
    }

    .success-badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .success-badge-sm {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    /* Button Styles */
    .btn-primary {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: inline-block !important;
        text-align: center !important;
    }

    .btn-primary:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    .btn-secondary {
        background: rgba(255, 255, 255, 0.1) !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: inline-block !important;
        text-align: center !important;
    }

    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    .btn-danger {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: inline-block !important;
        text-align: center !important;
    }

    .btn-danger:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
    }

    .btn-loading {
        background: linear-gradient(135deg, #64748b, #475569) !important;
        color: var(--text-secondary) !important;
        cursor: not-allowed !important;
        position: relative !important;
    }

    .btn-loading::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        margin: auto;
        border: 2px solid transparent;
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .error-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 0.4rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .info-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        padding: 0.4rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 1.5rem 0;
    }

    .form-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    @media (max-width: 768px) {
        .form-grid {
            grid-template-columns: 1fr;
        }
        .page-title h1 {
            font-size: 1.75rem !important;
        }
    }

    .warning-pulse {
        animation: pulse-red 1.5s ease-in-out infinite;
    }

    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 20px 10px rgba(239, 68, 68, 0.6); }
    }

    .warning-border {
        border: 3px solid #ef4444 !important;
        animation: pulse-border 1s ease-in-out infinite;
    }

    @keyframes pulse-border {
        0%, 100% { border-color: #ef4444 !important; }
        50% { border-color: #f87171 !important; }
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }

    .status-dot.green {
        background: #10b981;
        box-shadow: 0 0 8px #10b981;
    }

    .status-dot.red {
        background: #ef4444;
        box-shadow: 0 0 8px #ef4444;
        animation: blink 0.5s ease-in-out infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .warning-modal {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(239, 68, 68, 0.95);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        padding: 2rem;
        text-align: center;
    }

    .warning-icon {
        font-size: 5rem;
        margin-bottom: 1rem;
        animation: shake 0.5s ease-in-out infinite;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }

    .warning-text {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        max-width: 600px;
    }

    .calibration-circle {
        width: 100px;
        height: 100px;
        border: 3px solid #3b82f6;
        border-radius: 50%;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .calibration-dot {
        width: 20px;
        height: 20px;
        background: #3b82f6;
        border-radius: 50%;
    }

    .calibration-dot.active {
        background: #10b981;
        box-shadow: 0 0 15px #10b981;
    }

    .eye-preview {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        width: 160px;
        border-radius: 8px;
        border: 2px solid var(--border-color);
        z-index: 100;
    }

    .eye-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        z-index: 1000;
    }

    .strike-1 { border: 2px solid #ef4444; }
    .strike-2 { border: 4px solid #dc2626; }
    .strike-3 { border: 6px solid #b91c1c; }

    .termination-screen {
        background: #0a0e17;
        color: white;
        padding: 2rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def get_api_key(): 
    return os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")

def call_ai(messages, model=DEFAULT_MODEL, retries=3):
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key: 
        headers["Authorization"] = f"Bearer {api_key}"
    
    for attempt in range(retries):
        try:
            res = requests.post(
                f"{KILO_API_URL}/chat/completions", 
                headers=headers, 
                json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 1200}, 
                timeout=90
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                if attempt == retries - 1:
                    st.error(f"API Error ({res.status_code}): Unable to process request")
                time.sleep(1)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                st.error(f"Connection error: Unable to reach server")
    return None

def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages: 
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def create_pdf_report(info, evaluation, transcript, photo_bytes=None):
    pdf = FPDF()
    pdf.add_page()
    
    is_pass = "PASS" in str(evaluation).upper()
    decision_color = (16, 185, 129) if is_pass else (239, 68, 68)
    decision_text = "FINAL RESULT: PASS" if is_pass else "FINAL RESULT: FAIL"

    pdf.set_line_width(0.3)
    pdf.rect(5, 5, 200, 287)
    
    pdf.set_fill_color(10, 14, 23)
    pdf.rect(5, 5, 200, 45, 'F')
    
    try: 
        pdf.image(LOGO_PATH, 10, 10, 35, 35)
    except: 
        pass

    if photo_bytes:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(photo_bytes.getvalue())
            tmp_path = tmp.name
        try:
            pdf.image(tmp_path, 165, 10, 32, 32)
            os.unlink(tmp_path)
        except: 
            pass

    pdf.set_xy(50, 15)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, info.get('name', 'N/A').upper(), 0, 1)
    
    pdf.set_xy(50, 25)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(100, 6, f"ID: {info.get('id', 'N/A')} | EMAIL: {info.get('email', 'N/A')}", 0, 1)
    
    pdf.set_xy(50, 32)
    pdf.cell(100, 6, f"TIME: {st.session_state.interview_time}", 0, 1)

    pdf.set_fill_color(*decision_color)
    pdf.rect(5, 50, 200, 12, 'F')
    pdf.set_xy(5, 50)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 12, decision_text, 0, 1, 'C')

    pdf.set_xy(10, 75)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, 'SCREENING PERFORMANCE & EVALUATION', 'B', 1)
    pdf.ln(5)
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(0, 7, str(evaluation).encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, 'FULL INTERVIEW TRANSCRIPT', 'B', 1)
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(0, 6, str(transcript).encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.set_y(-15)
    pdf.set_font('Arial', 'I', 8)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 10, '© 2026 MANVER AI INTERVIEWER - CONFIDENTIAL CANDIDATE DATA', 0, 0, 'C')

    output = pdf.output(dest='S')
    if isinstance(output, str):
        return output.encode('latin-1')
    return output

if 'step' not in st.session_state: 
    st.session_state.step = 'setup'

if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}

# Initialize registration form fields
if 'reg_name' not in st.session_state:
    st.session_state.reg_name = ""
if 'reg_email' not in st.session_state:
    st.session_state.reg_email = ""
if 'reg_id' not in st.session_state:
    st.session_state.reg_id = ""
if 'reg_phone' not in st.session_state:
    st.session_state.reg_phone = ""

if 'user_info' in st.session_state:
    for key in ["name", "email", "phone", "id"]:
        if key not in st.session_state.user_info:
            st.session_state.user_info[key] = ""

if 'analysis' not in st.session_state: 
    st.session_state.analysis = ""
if 'questions' not in st.session_state: 
    st.session_state.questions = []
if 'answers' not in st.session_state: 
    st.session_state.answers = []
if 'current_q' not in st.session_state: 
    st.session_state.current_q = 0
if 'persistent_photo' not in st.session_state: 
    st.session_state.persistent_photo = None
if 'interview_time' not in st.session_state:
    st.session_state.interview_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
else:
    # Convert old format to new format if needed
    try:
        # Try to parse old format
        old_time = datetime.strptime(st.session_state.interview_time, "%Y-%m-%d %H:%M:%S")
        st.session_state.interview_time = old_time.strftime("%B %d, %Y at %I:%M %p")
    except ValueError:
        # Already in new format or other format, leave as is
        pass
if 'mic_verified' not in st.session_state:
    st.session_state.mic_verified = False
if 'photo_verified' not in st.session_state:
    st.session_state.photo_verified = False
if 'eye_tracker' not in st.session_state:
    st.session_state.eye_tracker = EyeTracker()
if 'eye_calibration_done' not in st.session_state:
    st.session_state.eye_calibration_done = False
if 'eye_tracking_active' not in st.session_state:
    st.session_state.eye_tracking_active = False
if 'eye_tracking_report' not in st.session_state:
    st.session_state.eye_tracking_report = None
if 'interview_terminated' not in st.session_state:
    st.session_state.interview_terminated = False

@st.dialog("Submit Interview?")
def confirm_submission():
    if st.session_state.get('submitting_interview', False):
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
                <h3 style="color: var(--text-primary);">Processing Your Interview...</h3>
                <p style="color: var(--text-secondary);">AI is analyzing your responses. Please wait.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important;">Ready to Submit?</h3>
            <p style="color: var(--text-secondary);">Once submitted, you won't be able to modify your answers.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")
    if c1.button("✅ Submit Interview", use_container_width=True, type="primary"):
        st.session_state.submitting_interview = True
        st.session_state.step = 'report'
        st.rerun()
    if c2.button("❌ Continue Interviewing", use_container_width=True):
        st.rerun()

def render_step_progress():
    """Render a horizontal progress bar for interview steps"""
    steps = [
        {"name": "Device Setup", "icon": "📷🎤", "step": "device_test", "description": "Test camera & microphone"},
        {"name": "Your Details", "icon": "👤", "step": "setup", "description": "Enter personal information"},
        {"name": "Resume Analysis", "icon": "📄", "step": "analysis", "description": "AI analyzes your profile"},
        {"name": "Live Interview", "icon": "🎯", "step": "interview", "description": "Answer technical questions"},
        {"name": "Final Results", "icon": "🏆", "step": "report", "description": "View evaluation report"}
    ]

    current_step = st.session_state.get('step', 'device_test')

    # Find current step index
    current_idx = 0
    for i, step in enumerate(steps):
        if step['step'] == current_step:
            current_idx = i
            break

    # Calculate progress percentage
    progress_percentage = ((current_idx + 1) / len(steps)) * 100

    # Get current step info
    current_step_info = steps[current_idx] if current_idx < len(steps) else steps[-1]

    # Build the progress bar HTML
    progress_html = f'''
        <div style="margin: 1rem 0; padding: 1.5rem; background: rgba(0,0,0,0.2); border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <div style="color: var(--text-primary); font-size: 1rem; font-weight: 700;">{current_step_info['name']}</div>
                    <div style="color: var(--text-secondary); font-size: 0.8rem;">{current_step_info['description']}</div>
                </div>
                <span style="color: var(--text-secondary); font-size: 0.8rem; background: rgba(255,255,255,0.1); padding: 0.25rem 0.75rem; border-radius: 20px;">{current_idx + 1} of {len(steps)}</span>
            </div>

            <!-- Progress Bar -->
            <div style="width: 100%; height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; margin-bottom: 1.5rem; overflow: hidden;">
                <div style="width: {progress_percentage}%; height: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); border-radius: 5px; transition: width 0.8s ease-in-out; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);"></div>
            </div>

            <!-- Step Indicators -->
            <div style="display: flex; justify-content: space-between; align-items: center;">
    '''

    for i, step in enumerate(steps):
        is_completed = i < current_idx
        is_current = i == current_idx
        is_pending = i > current_idx

        if is_completed:
            bg_color = "#10b981"
            icon_color = "white"
            status_indicator = "✓"
        elif is_current:
            bg_color = "#3b82f6"
            icon_color = "white"
            status_indicator = "●"
        else:
            bg_color = "rgba(100, 116, 139, 0.3)"
            icon_color = "#64748b"
            status_indicator = "○"

        progress_html += f'''
            <div style="display: flex; flex-direction: column; align-items: center; flex: 1; position: relative;">
                <div style="background: {bg_color}; border-radius: 50%; width: 2.8rem; height: 2.8rem; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; margin-bottom: 0.5rem; box-shadow: 0 3px 10px rgba(0,0,0,0.3); position: relative; z-index: 2; {'animation: pulse 2s infinite;' if is_current else ''}">
                    <span style="color: {icon_color}; line-height: 1;">{step['icon']}</span>
                </div>
                <div style="color: {bg_color if is_completed or is_current else '#64748b'}; font-size: 0.65rem; font-weight: 600; text-align: center; white-space: nowrap; max-width: 4rem;">
                    {step['name']}
                </div>
                <div style="color: {bg_color if is_completed else '#64748b'}; font-size: 0.9rem; margin-top: 0.25rem; opacity: 0.8;">
                    {status_indicator}
                </div>
            </div>
        '''

    progress_html += '''
            </div>
        </div>

        <style>
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        </style>
    '''

    for i, step in enumerate(steps):
        is_completed = i < current_idx
        is_current = i == current_idx
        is_pending = i > current_idx

        if is_completed:
            bg_color = "#10b981"
            icon_color = "white"
            status_indicator = "✓"
        elif is_current:
            bg_color = "#3b82f6"
            icon_color = "white"
            status_indicator = "●"
        else:
            bg_color = "rgba(100, 116, 139, 0.3)"
            icon_color = "#64748b"
            status_indicator = "○"

        progress_html += f'''
            <div style="display: flex; flex-direction: column; align-items: center; flex: 1; position: relative;">
                <div style="background: {bg_color}; border-radius: 50%; width: 2.5rem; height: 2.5rem; display: flex; align-items: center; justify-content: center; font-size: 1rem; margin-bottom: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.2); position: relative; z-index: 2;">
                    <span style="color: {icon_color}; line-height: 1;">{step['icon']}</span>
                </div>
                <div style="color: {bg_color if is_completed or is_current else '#64748b'}; font-size: 0.7rem; font-weight: 600; text-align: center; white-space: nowrap;">
                    {step['name']}
                </div>
                <div style="color: {bg_color if is_completed else '#64748b'}; font-size: 0.8rem; margin-top: 0.25rem;">
                    {status_indicator}
                </div>
            </div>
        '''

    progress_html += '''
            </div>
        </div>
    '''

    st.markdown(progress_html, unsafe_allow_html=True)

def render_header():
    if 'user_info' not in st.session_state or not st.session_state.user_info.get("name"): 
        return
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 2], gap="large")
    
    with col1:
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, width=70)
        else:
            st.image(LOGO_PATH, width=60)
            
    with col2:
        info = st.session_state.user_info
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; justify-content: center; text-align: center;">
                <div style="font-size: 1.25rem; font-weight: 700; color: #f1f5f9; letter-spacing: 0.5px; margin-bottom: 4px;">
                    {info['name'].upper()}
                </div>
                <div style="color: #64748b; font-size: 0.85rem; font-weight: 500; margin-bottom: 2px;">
                    ID: {info['id']}
                </div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 6px;">
                    {info['email']}
                </div>
                <div>
                    <span class="success-badge-sm">✓ VERIFIED</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 2px;">
                <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500;">
                    {st.session_state.interview_time}
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

def show_device_test():
    st.markdown("""
        <div id="main-content" style="text-align: center; margin-bottom: 2rem;">
            <h1 style="margin-bottom: 0.5rem;">📷 Test Camera & Microphone</h1>
            <p style="color: var(--text-secondary);">Verify your devices are working before the interview</p>
        </div>
    """, unsafe_allow_html=True)
    
    step = st.session_state.get("device_test_step", 0)
    
    if step == 0:
        st.markdown("""
            <div class="card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎥</div>
                <h3 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important;">Device Permissions Required</h3>
                <p style="color: var(--text-secondary); margin: 1rem 0;">
                    We need access to your camera and microphone to conduct the video interview and verify your identity.
                </p>
                <p style="color: var(--text-muted); font-size: 0.85rem;">
                    Click below to grant browser permissions. You will be prompted to allow camera and microphone access.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔓 Enable Camera & Microphone", type="primary", use_container_width=True):
            st.session_state.device_test_step = 1
            st.rerun()
        
        if st.button("Go Back", use_container_width=True):
            st.session_state.device_test_step = 0
            st.rerun()
    
    elif step == 1:
        st.markdown("""
            <script>
            async function checkPermissions() {
                const camPerm = await navigator.permissions.query({name: 'camera'});
                const micPerm = await navigator.permissions.query({name: 'microphone'});
                const results = {
                    camera: camPerm.state,
                    microphone: micPerm.state
                };
                window.parent.postMessage({type: 'permissionCheck', results: results}, '*');
            }
            checkPermissions();
            </script>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📷</div>
                    <h4 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important;">Camera</h4>
                    <p style="color: var(--text-muted); font-size: 0.8rem;">Verify your camera is working</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <button id="start-camera-btn" onclick="startCamera()" style="
                    background: linear-gradient(135deg, #3b82f6, #2563eb);
                    color: white; border: none; padding: 0.75rem 1.5rem;
                    border-radius: 10px; font-weight: 600; cursor: pointer;
                    width: 100%; margin-top: 1rem;
                ">Start Camera Preview</button>
                <video id="camera-preview" autoplay playsinline style="display: none; width: 100%; border-radius: 10px; margin-top: 1rem;"></video>
                <canvas id="camera-canvas" style="display: none;"></canvas>
                <script>
                let cameraStream = null;
                async function startCamera() {
                    try {
                        cameraStream = await navigator.mediaDevices.getUserMedia({video: true, audio: false});
                        const video = document.getElementById('camera-preview');
                        video.srcObject = cameraStream;
                        video.style.display = 'block';
                        document.getElementById('start-camera-btn').style.display = 'none';
                        window.parent.postMessage({type: 'cameraStarted', success: true}, '*');
                    } catch(err) {
                        alert('Camera access denied or not available: ' + err.message);
                        window.parent.postMessage({type: 'cameraStarted', success: false, error: err.message}, '*');
                    }
                }
                </script>
            """, unsafe_allow_html=True)
            
            st.markdown('<span class="info-badge" id="camera-status">⏳ Checking...</span>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🎤</div>
                    <h4 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important;">Microphone</h4>
                    <p style="color: var(--text-muted); font-size: 0.8rem;">Test your microphone input</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <button id="start-mic-btn" onclick="startMicrophone()" style="
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white; border: none; padding: 0.75rem 1.5rem;
                    border-radius: 10px; font-weight: 600; cursor: pointer;
                    width: 100%; margin-top: 1rem;
                ">Start Microphone Test</button>
                <canvas id="mic-visualizer" style="display: none; width: 100%; height: 60px; background: rgba(0,0,0,0.3); border-radius: 8px; margin-top: 1rem;"></canvas>
                <p id="mic-level" style="display: none; text-align: center; color: var(--text-secondary); font-size: 0.85rem;">Listening...</p>
                <script>
                let audioContext = null;
                let micStream = null;
                async function startMicrophone() {
                    try {
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        micStream = await navigator.mediaDevices.getUserMedia({audio: true});
                        const source = audioContext.createMediaStreamSource(micStream);
                        const analyser = audioContext.createAnalyser();
                        analyser.fftSize = 256;
                        source.connect(analyser);
                        
                        const canvas = document.getElementById('mic-visualizer');
                        canvas.style.display = 'block';
                        document.getElementById('mic-level').style.display = 'block';
                        document.getElementById('start-mic-btn').style.display = 'none';
                        
                        const ctx = canvas.getContext('2d');
                        const bufferLength = analyser.frequencyBinCount;
                        const dataArray = new Uint8Array(bufferLength);
                        
                        function draw() {
                            requestAnimationFrame(draw);
                            analyser.getByteFrequencyData(dataArray);
                            ctx.fillStyle = 'rgba(0,0,0,0.2)';
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                            const barWidth = (canvas.width / bufferLength) * 2.5;
                            let x = 0;
                            for(let i = 0; i < bufferLength; i++) {
                                const barHeight = dataArray[i] / 2;
                                ctx.fillStyle = 'rgb(' + (dataArray[i] + 100) + ',200,50)';
                                ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                                x += barWidth + 1;
                            }
                        }
                        draw();
                        window.parent.postMessage({type: 'micStarted', success: true}, '*');
                    } catch(err) {
                        alert('Microphone access denied or not available: ' + err.message);
                        window.parent.postMessage({type: 'micStarted', success: false, error: err.message}, '*');
                    }
                }
                </script>
            """, unsafe_allow_html=True)
            
            st.markdown('<span class="info-badge" id="mic-status">⏳ Checking...</span>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        col_done, col_back = st.columns([2, 1], gap="medium")
        with col_done:
            if st.button("✅ Done - Continue to Photo", type="primary", use_container_width=True):
                st.session_state.device_test_done = True
                st.session_state.device_permissions_granted = True
                st.session_state.step = 'photo_capture'
                st.rerun()
        with col_back:
            if st.button("← Back", use_container_width=True):
                st.session_state.device_test_step = 0
                st.rerun()

def show_photo_capture():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="margin-bottom: 0.5rem;">📸 Identity Verification</h1>
            <p style="color: var(--text-secondary);">Capture your photograph for identity verification</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_cam, col_info = st.columns([1, 1], gap="large")
    
    with col_cam:
        st.markdown("""
            <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="color: var(--accent-cyan); font-weight: 600; margin-bottom: 1rem;">
                    📸 Capturing your photograph...
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        photo_cam = st.camera_input(
            "Capture Photo", 
            key="photo_capture_cam",
            label_visibility="collapsed"
        )
        
        if photo_cam:
            st.session_state.persistent_photo = photo_cam
            st.session_state.photo_verified = True
            st.markdown('<span class="success-badge">✓ Photo Captured!</span>', unsafe_allow_html=True)
            st.image(photo_cam, width=200)
    
    with col_info:
        st.markdown("""
            <div class="card">
                <h3 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important; margin-bottom: 1rem;">
                    Photo Guidelines
                </h3>
                <ul style="color: var(--text-secondary); line-height: 1.8; padding-left: 1rem;">
                    <li>Ensure your face is clearly visible</li>
                    <li>Good lighting on your face</li>
                    <li>Remove glasses or sunglasses</li>
                    <li>Look directly at the camera</li>
                    <li>Neutral expression preferred</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("photo_verified") and st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.mic_verified = True
            st.session_state.device_test_done = True
            st.session_state.device_permissions_granted = True
            st.session_state.step = 'eye_calibration'
            st.rerun()
        
        if st.button("← Go Back", use_container_width=True):
            st.session_state.step = 'device_test'
            st.rerun()

def show_eye_calibration():
    tracker = st.session_state.get('eye_tracker')
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h1 style="margin-bottom: 0.5rem;">👁️ Eye Tracking Calibration</h1>
            <p style="color: var(--text-secondary);">Look directly at the camera and follow the instructions</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_info, col_cam = st.columns([1, 1.5], gap="large")
    
    with col_info:
        st.markdown("""
            <div class="card">
                <h3 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important; margin-bottom: 1rem;">
                    Calibration Instructions
                </h3>
                <ul style="color: var(--text-secondary); line-height: 1.8; padding-left: 1rem;">
                    <li>Sit at a comfortable distance from your camera (arm's length)</li>
                    <li>Keep your head straight and look directly at the screen</li>
                    <li>Remove glasses if possible for better accuracy</li>
                    <li>Ensure good lighting on your face</li>
                    <li>Stay still during calibration (about 3 seconds)</li>
                </ul>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
                    <p style="color: var(--accent-blue); font-weight: 500; margin: 0;">
                        ⚠️ Eye tracking will monitor your gaze throughout the interview. 
                        Looking away from the screen may result in warnings or session termination.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('eye_calibration_done'):
            st.markdown("""
                <div style="text-align: center; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 8px; border: 1px solid #10b981;">
                    <span style="font-size: 2rem;">✅</span>
                    <p style="color: #10b981; font-weight: 600; margin-top: 0.5rem;">Calibration Complete!</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col_cam:
        frame_data = st.camera_input(
            "Position your face in the center",
            key="calibration_camera",
            label_visibility="collapsed"
        )
        
        if frame_data is not None:
            import cv2
            import numpy as np
            from io import BytesIO
            
            bytes_data = frame_data.getvalue()
            frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            if tracker:
                success = tracker.calibrate(frame)
                if success:
                    st.session_state.eye_calibration_done = True
                    st.session_state.eye_tracking_active = True
                    tracker.state.is_active = True
                    st.success("Calibration successful!")
                    time.sleep(0.5)
                    st.rerun()
        
        if st.session_state.get('eye_calibration_done'):
            if st.button("Continue to Interview Setup →", type="primary", use_container_width=True):
                st.session_state.step = 'setup'
                st.rerun()
        else:
            if st.button("Skip Calibration", use_container_width=True):
                st.session_state.eye_calibration_done = True
                st.session_state.step = 'setup'
                st.rerun()

def show_setup():
    st.markdown("""
        <div class="logo-container" style="margin-top: -1rem;">
            <img src="data:image/png;base64,{LOGO_BASE64}" width="80">
            <div class="logo-text">
                <h1>MANVER <span style="color: #06b6d4;">AI INTERVIEWER</span></h1>
                <p>Advanced AI Interview Platform</p>
            </div>
        </div>
    """.format(LOGO_BASE64=LOGO_BASE64), unsafe_allow_html=True)
    
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, transparent, #3b82f6, transparent); margin: 0.5rem 0 2rem;"></div>', unsafe_allow_html=True)
    
    col_main, col_side = st.columns([2, 1], gap="large")
    
    with col_main:
        with st.container():
            st.markdown("""
                <div class="card-header">
                    <span class="card-icon">🔑</span>
                    <span class="card-title">Candidate Information</span>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1], gap="medium")
            with c1:
                name_val = st.session_state.get("reg_name", "")
                email_val = st.session_state.get("reg_email", "")
                st.text_input("Full Name *", key="reg_name", placeholder="e.g. John Doe",
                            help="Enter your full legal name as it appears on official documents")
                if name_val and len(name_val.strip()) < 2:
                    st.error("⚠️ Full name must be at least 2 characters")
                elif name_val and not any(c.isalpha() for c in name_val):
                    st.error("⚠️ Full name must contain letters")

                st.text_input("Email ID *", key="reg_email", placeholder="john@example.com",
                            help="Enter a valid email address for communication")
                if email_val and "@" not in email_val:
                    st.error("⚠️ Please enter a valid email address")

            with c2:
                id_val = st.session_state.get("reg_id", "")
                phone_val = st.session_state.get("reg_phone", "")
                st.text_input("Candidate ID *", key="reg_id", placeholder="e.g. CAND-001",
                            help="Enter your unique candidate identification number")
                if id_val and len(id_val.strip()) < 3:
                    st.error("⚠️ Candidate ID must be at least 3 characters")

                st.text_input("Phone Number *", key="reg_phone", placeholder="+91 XXXX XXXX",
                            help="Enter your phone number with country code")
                if phone_val and not any(c.isdigit() for c in phone_val):
                    st.error("⚠️ Phone number must contain digits")
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="card-header">
                    <span class="card-icon">📄</span>
                    <span class="card-title">Assessment Basis</span>
                </div>
            """, unsafe_allow_html=True)
            
            input_type = st.radio(
                "Choose Input Type:",
                ["Upload Resume (PDF)", "Paste Job Description (JD)"],
                horizontal=True,
                label_visibility="collapsed"
            )
            
            uploaded_file = None
            jd_text = ""
            
            if input_type == "Upload Resume (PDF)":
                uploaded_file = st.file_uploader("", type=['pdf'], label_visibility="collapsed", help="Upload your resume in PDF format")
                if uploaded_file is not None:
                    file_size = uploaded_file.size / 1024
                    st.markdown(f"""
                        <div class="file-selected">
                            <span class="file-selected-icon">✅</span>
                            <div class="file-selected-info">
                                <div class="file-selected-name">{uploaded_file.name}</div>
                                <div class="file-selected-size">{file_size:.1f} KB</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                jd_text = st.text_area("Paste Job Description (JD) *", height=120, placeholder="Example: Senior Software Engineer with 5+ years experience...", label_visibility="collapsed")
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="card-header">
                    <span class="card-icon">🧠</span>
                    <span class="card-title">Intelligence Model</span>
                </div>
            """, unsafe_allow_html=True)
            
            model = st.selectbox(
                "Intelligence Model",
                st.session_state.get("available_models", ["kilo-auto/free"]),
                label_visibility="visible",
                help="Select the AI model to use for interview"
            )
            
            if st.button("🚀 Start Interview Session", type="primary", use_container_width=True):
                v_name = st.session_state.get("reg_name", "")
                v_id = st.session_state.get("reg_id", "")
                v_email = st.session_state.get("reg_email", "")
                v_phone = st.session_state.get("reg_phone", "")
                
                v_name = str(v_name).strip() if v_name is not None else ""
                v_id = str(v_id).strip() if v_id is not None else ""
                v_email = str(v_email).strip() if v_email is not None else ""
                v_phone = str(v_phone).strip() if v_phone is not None else ""
                
                missing_fields = []
                if not v_name:
                    missing_fields.append("Full Name")
                if not v_email:
                    missing_fields.append("Email ID")
                if not v_id:
                    missing_fields.append("Candidate ID")
                if not v_phone:
                    missing_fields.append("Phone Number")

                if missing_fields:
                    st.error(f"⚠️ Please fill the following required fields: {', '.join(missing_fields)}")
                elif input_type == "Upload Resume (PDF)" and (uploaded_file is None):
                    st.error("📄 Please upload your resume PDF.")
                elif input_type == "Paste Job Description (JD)" and (not jd_text or not jd_text.strip()):
                    st.error("📝 Please paste the Job Description.")
                elif not st.session_state.get("photo_verified"):
                    st.error("📸 Identity verification required. Capture your photo.")
                elif not st.session_state.get("mic_verified"):
                    st.error("🎤 Microphone verification required. Record a test audio.")
                else:
                    st.session_state.user_info = {
                        "name": v_name, 
                        "id": v_id, 
                        "email": v_email, 
                        "phone": v_phone
                    }
                    st.session_state.interview_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
                    
                    show_loading_overlay("🧠 Analyzing Your Information<br><small>AI is processing your resume/job description and preparing personalized questions...</small>", spinner=True)

                    with st.spinner(""):
                        if input_type == "Upload Resume (PDF)":
                            input_content = extract_text_from_pdf(uploaded_file)
                            prompt_msg = "Analyze this resume and identify key skills, experience, and qualifications. Provide a detailed summary."
                        else:
                            input_content = jd_text
                            prompt_msg = "Analyze this job description and identify key skills, requirements, and qualifications needed. DO NOT INCLUDE ANY LINKS OR URLs."
                        
                        res = safe_api_call(call_ai, [{"role": "system", "content": prompt_msg}, {"role": "user", "content": input_content}], model=model)
                        if res:
                            st.session_state.analysis = res
                            st.session_state.step = 'analysis'
                            st.rerun()
    
    with col_side:
        with st.container():
            st.markdown("""
                <div class="card-header">
                    <span class="card-icon">🎙️</span>
                    <span class="card-title">System Verification</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div style="background: rgba(59, 130, 246, 0.08); padding: 0.5rem; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.15); margin-bottom: 0.75rem;">
                    <div style="color: #60a5fa; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.25rem;">
                        🎤 Mic Check
                    </div>
                    <div style="color: #64748b; font-size: 0.7rem;">
                        Record 1-2 sec to verify mic.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            mic_test = st.audio_input("Test Microphone", key="mic_test_recording", label_visibility="collapsed")
            if mic_test:
                st.session_state.mic_verified = True
                st.markdown('<span class="success-badge">✓ Ready</span>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin: 0.75rem 0;"></div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div style="background: rgba(6, 182, 212, 0.08); padding: 0.5rem; border-radius: 8px; border: 1px solid rgba(6, 182, 212, 0.15); margin-bottom: 0.75rem;">
                    <div style="color: #06b6d4; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.25rem;">
                        📸 Photo ID
                    </div>
                    <div style="color: #64748b; font-size: 0.7rem;">
                        Take your photo for verification.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            def sync_photo():
                if st.session_state.setup_cam is None:
                    st.session_state.persistent_photo = None
                    st.session_state.photo_verified = False
                else:
                    st.session_state.persistent_photo = st.session_state.setup_cam
                    st.session_state.photo_verified = True
                    
            st.camera_input("Take Photo", key="setup_cam", label_visibility="collapsed", on_change=sync_photo)
            
            if st.session_state.get("photo_verified") and st.session_state.persistent_photo:
                st.image(st.session_state.persistent_photo, width=120)
                st.markdown('<span class="success-badge">✓ Captured</span>', unsafe_allow_html=True)

def show_analysis():
    render_header()
    render_step_progress()

    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: var(--text-primary); margin-bottom: 0.5rem;">CANDIDATE INSIGHTS</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">Reviewing candidate information and assessment</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_img, col_details = st.columns([1, 2], gap="large")
    
    with col_img:
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, use_container_width=True)
            st.markdown("""
                <style>
                    [data-testid="stImage"] img {
                        aspect-ratio: 1 / 1;
                        object-fit: cover;
                        border-radius: 14px;
                        border: 2px solid #3b82f6;
                    }
                </style>
            """, unsafe_allow_html=True)
    
    with col_details:
        info = st.session_state.user_info
        st.markdown(f"""
            <div class="card" style="margin-bottom: 1.5rem;">
                <table style="width: 100%; color: #f1f5f9; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 12px 0; color: #64748b; font-weight: 500; width: 30%; font-size: 0.85rem;">FULL NAME</td>
                        <td style="font-size: 1.1rem; font-weight: 700;">{info['name'].upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #64748b; font-weight: 500; font-size: 0.85rem;">CANDIDATE ID</td>
                        <td style="font-weight: 600; color: #06b6d4;">{info['id']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #64748b; font-weight: 500; font-size: 0.85rem;">EMAIL</td>
                        <td>{info['email']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 0; color: #64748b; font-weight: 500; font-size: 0.85rem;">PHONE</td>
                        <td>{info['phone']}</td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📋 View Analysis Summary", expanded=False):
            analysis_text = st.session_state.get('analysis', '').strip()
            if analysis_text:
                st.markdown(f"""
                    <div style="color: #cbd5e1; line-height: 1.7; font-size: 0.95rem;">
                        {analysis_text}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Analysis data is not available. Please go back to the setup step and try again.")
    
    st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        analysis_text = st.session_state.get('analysis', '').strip()
        if not analysis_text:
            st.error("❌ Cannot proceed without analysis data. Please return to setup and try again.")
        elif st.button("✅ Confirm & Proceed to Interview", type="primary", use_container_width=True):
            show_loading_overlay("🎯 Preparing Your Interview<br><small>Generating personalized technical questions based on your profile...</small>", spinner=True)

            with st.spinner(""):
                prompt = "Generate exactly 8 specific, high-level technical interview questions based on the provided skills. One question per line. No numbering. Make them challenging and relevant to the role."
                text = safe_api_call(call_ai, [{"role": "system", "content": prompt}, {"role": "user", "content": analysis_text}])
                if text:
                    questions = [q.strip() for q in text.split('\n') if len(q.strip()) > 15][:8]
                    if len(questions) < 5:
                        questions = [
                            "Describe your experience with system design and architecture patterns.",
                            "How do you approach debugging complex production issues?",
                            "Explain your strategy for optimizing application performance.",
                            "What is your experience with cloud services and infrastructure?",
                            "How do you ensure code quality and maintainability?",
                            "Describe a challenging technical problem you solved.",
                            "How do you stay updated with emerging technologies?",
                            "Explain your approach to security best practices."
                        ][:8]
                    st.session_state.questions = questions
                    st.session_state.answers = [""] * len(questions)
                    st.session_state.current_q = 0
                    st.session_state.step = 'interview'
                    st.rerun()

@st.fragment
def interview_content():
    tracker = st.session_state.get('eye_tracker')
    
    if tracker and st.session_state.get('eye_tracking_active'):
        warning_info = tracker.get_warning_info()
        
        if warning_info and tracker.state.strikes >= 1:
            strike_num = tracker.state.strikes
            
            if strike_num == 1:
                st.markdown("""
                    <div class="warning-modal" style="background: rgba(239, 68, 68, 0.15); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; animation: pulse-red 1.5s ease-in-out infinite;">
                        <div style="font-size: 2rem;">⚠️</div>
                        <p style="color: #ef4444; font-weight: 600;">Please keep your eyes on the screen. This is your first warning.</p>
                    </div>
                """, unsafe_allow_html=True)
            elif strike_num == 2:
                st.markdown("""
                    <div class="warning-modal" style="background: rgba(239, 68, 68, 0.25); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; border: 2px solid #ef4444; animation: pulse-red 1s ease-in-out infinite;">
                        <div style="font-size: 2.5rem;">🚨</div>
                        <p style="color: #ef4444; font-weight: 600; font-size: 1.1rem;">Warning: Looking away from the screen is considered cheating. One more violation and your interview may be terminated.</p>
                    </div>
                """, unsafe_allow_html=True)
            elif strike_num == 3:
                st.markdown("""
                    <div class="warning-modal" style="background: rgba(239, 68, 68, 0.35); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem; border: 3px solid #dc2626; animation: shake 0.3s ease-in-out infinite;">
                        <div style="font-size: 3rem;">🛑</div>
                        <p style="color: #ef4444; font-weight: 700; font-size: 1.2rem;">Final Warning Detected. If you look away from the screen again, your interview will be immediately stopped and your session will be permanently terminated.</p>
                    </div>
                """, unsafe_allow_html=True)
            elif strike_num >= 4:
                st.session_state.interview_terminated = True
                tracker.state.is_active = False
                st.markdown("""
                    <div class="termination-screen">
                        <div style="font-size: 4rem;">❌</div>
                        <h1 style="color: #ef4444; font-size: 2rem; margin-top: 1rem;">Interview Terminated</h1>
                        <p style="color: #94a3b8; margin-top: 1rem;">You have been flagged for repeated eye-tracking violations.</p>
                        <p style="color: #64748b; margin-top: 2rem;">This incident has been logged and reported.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.session_state.step = 'report'
                st.rerun()
    
    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    col_qa, col_proc = st.columns([2, 1], gap="large")
    
    with col_qa:
        progress_text = f"Question {q_idx + 1} of {total}"
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="info-badge">INTERVIEW IN PROGRESS</span>
                <span style="color: #64748b; font-size: 0.85rem; font-weight: 500;">{progress_text}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.progress((q_idx + 1) / total)
        
        st.markdown(f"""
            <div class="question-card" style="margin-bottom: 1.5rem;">
                <div style="font-size: 1.4rem; font-weight: 700; color: #f1f5f9; line-height: 1.5;">
                    {st.session_state.questions[q_idx]}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Custom text area with microphone icon
        current_answer = st.session_state.answers[q_idx]

        text_area_html = f'''
        <div style="position: relative;">
            <textarea
                id="answer-textarea-{q_idx}"
                placeholder="Type your answer here... Click the microphone to use voice input"
                style="
                    width: 100%;
                    min-height: 220px;
                    padding: 1rem;
                    padding-right: 3rem;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    background: rgba(0, 0, 0, 0.3);
                    color: var(--text-primary);
                    font-family: inherit;
                    font-size: 0.95rem;
                    line-height: 1.5;
                    resize: vertical;
                    outline: none;
                "
                oninput="updateTextAreaValue(this.value, {q_idx})"
            >{current_answer}</textarea>

            <button
                id="mic-btn-{q_idx}"
                onclick="toggleVoiceInput({q_idx})"
                style="
                    position: absolute;
                    top: 1rem;
                    right: 1rem;
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 6px;
                    width: 2rem;
                    height: 2rem;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #10b981;
                    font-size: 1rem;
                    transition: all 0.2s;
                "
                onmouseover="this.style.background='rgba(16, 185, 129, 0.2)'; this.style.borderColor='rgba(16, 185, 129, 0.5)';"
                onmouseout="this.style.background='rgba(16, 185, 129, 0.1)'; this.style.borderColor='rgba(16, 185, 129, 0.3)';"
                title="Click to start voice input"
            >
                🎤
            </button>
        </div>

        <script>
        let recognition_{q_idx} = null;
        let isListening_{q_idx} = false;

        function updateTextAreaValue(value, qIdx) {{
            // Update Streamlit session state
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                dataType: 'string',
                value: value,
                key: 'answer_' + qIdx
            }}, '*');
        }}

        function toggleVoiceInput(qIdx) {{
            const micBtn = document.getElementById('mic-btn-' + qIdx);
            const textarea = document.getElementById('answer-textarea-' + qIdx);

            if (!isListening_{q_idx}) {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {{
                    alert('Voice input not supported in this browser');
                    return;
                }}

                recognition_{q_idx} = new SpeechRecognition();
                recognition_{q_idx}.continuous = false;
                recognition_{q_idx}.interimResults = false;
                recognition_{q_idx}.lang = 'en-US';

                recognition_{q_idx}.onstart = function() {{
                    isListening_{q_idx} = true;
                    micBtn.innerHTML = '🛑';
                    micBtn.style.background = 'rgba(239, 68, 68, 0.2)';
                    micBtn.style.borderColor = 'rgba(239, 68, 68, 0.5)';
                    micBtn.style.color = '#ef4444';
                    micBtn.title = 'Click to stop voice input';
                }};

                recognition_{q_idx}.onresult = function(event) {{
                    const transcript = event.results[0][0].transcript;
                    const currentValue = textarea.value;
                    textarea.value = currentValue ? currentValue + ' ' + transcript : transcript;
                    updateTextAreaValue(textarea.value, qIdx);
                    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }};

                recognition_{q_idx}.onend = function() {{
                    isListening_{q_idx} = false;
                    micBtn.innerHTML = '🎤';
                    micBtn.style.background = 'rgba(16, 185, 129, 0.1)';
                    micBtn.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                    micBtn.style.color = '#10b981';
                    micBtn.title = 'Click to start voice input';
                }};

                recognition_{q_idx}.onerror = function() {{
                    isListening_{q_idx} = false;
                    micBtn.innerHTML = '🎤';
                    micBtn.style.background = 'rgba(16, 185, 129, 0.1)';
                    micBtn.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                    micBtn.style.color = '#10b981';
                }};

                recognition_{q_idx}.start();
            }} else {{
                if (recognition_{q_idx}) {{
                    recognition_{q_idx}.stop();
                }}
            }}
        }}
        </script>
        '''

        st.markdown(text_area_html, unsafe_allow_html=True)

        # Get updated value from the custom textarea
        updated_value = st.session_state.get(f'answer_{q_idx}', current_answer)
        st.session_state.answers[q_idx] = updated_value

        col_back, _, col_next = st.columns([1, 0.2, 1.2], gap="medium")

        with col_back:
            if st.button("⬅️ Previous", disabled=(q_idx == 0), use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()

        with col_next:
            label = "Finish Interview ✨" if q_idx + 1 == total else "Next Question ➡️"
            if st.button(label, use_container_width=True, type="primary"):
                if q_idx + 1 < total:
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    confirm_submission()
    
    with col_proc:
        tracker = st.session_state.get('eye_tracker')
        strikes = tracker.state.strikes if tracker else 0
        
        st.markdown("""
            <div style="color: #64748b; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.75rem; letter-spacing: 0.5px;">
                📹 PROCTORING
            </div>
        """, unsafe_allow_html=True)
        
        # Optimize camera handling - use consistent key to reduce restarts
        camera_key = "interview_camera"  # Use consistent key across questions
        st.markdown('<div class="proctor-card" style="padding: 0.25rem;">', unsafe_allow_html=True)
        proctor_frame = st.camera_input("Monitoring", key=camera_key, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if proctor_frame is not None and tracker and st.session_state.get('eye_tracking_active'):
            import cv2
            import numpy as np
            from io import BytesIO
            
            bytes_data = proctor_frame.getvalue()
            frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            gaze_result = tracker.process_frame(frame)
            
            if gaze_result.get("is_looking_away"):
                pass
        
        if strikes > 0:
            status_color = "#ef4444" if strikes > 0 else "#10b981"
            status_text = "WARNING" if strikes < 3 else "TERMINATED"
            st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 0.4rem; border-radius: 6px; margin-top: 0.5rem; font-size: 0.6rem; font-weight: 600; text-align: center;">
                    ⚠️ STRIKE {strikes}/4
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 0.4rem; border-radius: 6px; margin-top: 0.5rem; font-size: 0.6rem; font-weight: 600; text-align: center;">
                    🛡️ COMPLIANT
                </div>
            """, unsafe_allow_html=True)

def show_interview():
    render_header()
    render_step_progress()
    interview_content()

def show_report():
    info = st.session_state.user_info
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <span class="info-badge">FINAL RESULTS</span>
            <h1 style="margin-top: 0.5rem;">EVALUATION REPORT</h1>
        </div>
    """, unsafe_allow_html=True)
    
    show_loading_overlay("📊 Evaluating Your Performance<br><small>AI is analyzing your responses, communication skills, and technical knowledge...</small>", spinner=True)

    with st.spinner(""):
        transcript = ""
        for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
            transcript += f"Q{i+1}: {q}\nA: {a}\n\n"
            
        res = safe_api_call(call_ai, [
            {"role": "system", "content": "You are an expert technical interviewer. Evaluate the candidate's interview responses. You MUST START your response with either 'RESULT: PASS' or 'RESULT: FAIL' based on the overall quality of answers, then provide detailed feedback including strengths, areas for improvement, and a final recommendation."},
            {"role": "user", "content": f"Candidate: {info.get('name', 'N/A')}\nID: {info.get('id', 'N/A')}\nEmail: {info.get('email', 'N/A')}\nDate: {st.session_state.interview_time}\n\nInterview Transcript:\n{transcript}"}
        ])
    
    is_pass = "PASS" in str(res).upper()
    
    col_result, col_candidate = st.columns([1, 1], gap="large")
    
    with col_result:
        if is_pass:
            st.markdown("""
                <div class="result-pass">
                    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">🎉</div>
                    <div style="font-size: 1.75rem; font-weight: 800; letter-spacing: 2px;">RESULT: PASS</div>
                    <div style="color: #10b981; font-size: 0.9rem; margin-top: 0.5rem;">Congratulations on successfully completing the interview!</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="result-fail">
                    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem;">📋</div>
                    <div style="font-size: 1.75rem; font-weight: 800; letter-spacing: 2px;">RESULT: FAIL</div>
                    <div style="color: #ef4444; font-size: 0.9rem; margin-top: 0.5rem;">Thank you for your time. We encourage you to apply again.</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="card" style="margin-top: 1.5rem;">
                <div class="card-header">
                    <span class="card-icon">📋</span>
                    <span class="card-title">Detailed Analysis</span>
                </div>
            """, unsafe_allow_html=True)
        
        if res:
            analysis_text = res.replace("RESULT: PASS", "").replace("RESULT: FAIL", "").strip()
            st.markdown(f"""
                <div style="color: #cbd5e1; line-height: 1.8; font-size: 0.95rem;">
                    {analysis_text}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="color: #94a3b8; line-height: 1.8; font-size: 0.95rem;">
                    Interview completed successfully. The AI analysis is being processed. 
                    Your responses have been recorded and will be reviewed by our team.
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        
        with st.expander("📝 View Full Interview Transcript", expanded=False):
            for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                st.markdown(f"**Q{i+1}:** {q}")
                st.markdown(f"**A:** {a if a else '_No answer provided_'}")
                st.markdown("---")
        
        tracker = st.session_state.get('eye_tracker')
        if tracker and st.session_state.get('eye_tracking_active'):
            report = tracker.generate_report()
            st.session_state.eye_tracking_report = report
            
            with st.expander("👁️ Eye Tracking Integrity Report", expanded=True):
                score = report.get('compliance_score', 0)
                strikes = report.get('strikes', 0)
                total_events = report.get('total_events', 0)
                
                score_color = "#10b981" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"
                
                st.markdown(f"""
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                        <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 12px;">
                            <div style="font-size: 2rem; font-weight: 700; color: {score_color};">{score:.0f}%</div>
                            <div style="color: #94a3b8; font-size: 0.85rem;">Compliance Score</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 12px;">
                            <div style="font-size: 2rem; font-weight: 700; color: {'#ef4444' if strikes > 0 else '#10b981'};">{strikes}/4</div>
                            <div style="color: #94a3b8; font-size: 0.85rem;">Warnings Issued</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 12px;">
                            <div style="font-size: 2rem; font-weight: 700; color: #3b82f6;">{total_events}</div>
                            <div style="color: #94a3b8; font-size: 0.85rem;">Gaze Events</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                tracking_time = report.get('total_tracking_time', 0)
                away_time = report.get('away_time', 0)
                
                if tracking_time > 0:
                    away_pct = (away_time / tracking_time) * 100
                    st.markdown(f"""
                        <div style="color: #94a3b8; font-size: 0.9rem;">
                            <p><strong>Total Tracking Time:</strong> {tracking_time:.1f}s</p>
                            <p><strong>Time Looking Away:</strong> {away_time:.1f}s ({away_pct:.1f}%)</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                if strikes >= 4:
                    st.markdown("""
                        <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                            <p style="color: #ef4444; font-weight: 600; margin: 0;">⚠️ Interview terminated due to eye-tracking violations</p>
                        </div>
                    """, unsafe_allow_html=True)
    
    with col_candidate:
        st.markdown("""
            <div class="card-header">
                <span class="card-icon">👤</span>
                <span class="card-title">Candidate</span>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, use_container_width=True)
        
        st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Name</div>
                <div style="color: #f1f5f9; font-weight: 700; font-size: 1.1rem;">{info.get('name', 'N/A')}</div>
                
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 1rem;">ID</div>
                <div style="color: #06b6d4; font-weight: 600;">{info.get('id', 'N/A')}</div>
                
                <div style="color: #64748b; font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 1rem;">Date</div>
                <div style="color: #94a3b8;">{st.session_state.interview_time}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
        
        if st.button("🔄 Start New Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

step = st.session_state.get('step', 'device_test')

if step == 'device_test':
    show_device_test()
elif step == 'photo_capture':
    show_photo_capture()
elif step == 'eye_calibration':
    show_eye_calibration()
elif step == 'device_test_complete' or step == 'setup': 
    show_setup()
elif step == 'analysis': 
    show_analysis()
elif step == 'interview': 
    show_interview()
elif step == 'report': 
    show_report()
