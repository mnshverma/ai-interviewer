import streamlit as st
import os
import requests
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import time
from fpdf import FPDF
from datetime import datetime
import base64

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

if 'available_models' not in st.session_state:
    st.session_state.available_models = get_free_models()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2332;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: rgba(255, 255, 255, 0.08);
    }

    * {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: var(--bg-primary);
        background-image: 
            radial-gradient(ellipse at 20% 0%, rgba(59, 130, 246, 0.12) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(6, 182, 212, 0.08) 0%, transparent 50%);
        min-height: 100vh;
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
        font-size: 2.25rem !important;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #60a5fa 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2 {
        font-size: 1.5rem !important;
        color: var(--accent-cyan) !important;
        -webkit-text-fill-color: var(--accent-cyan);
    }

    h3 {
        font-size: 1.15rem !important;
        color: var(--text-secondary) !important;
        -webkit-text-fill-color: var(--text-secondary);
    }

    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.75rem;
        backdrop-filter: blur(12px);
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }

    .card-icon {
        font-size: 1.5rem;
    }

    .card-title {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 1.1rem;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        padding: 0.875rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }

    .stSelectbox > label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }

    .stSelectbox [data-baseweb="select"] > div {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
    }

    .stSelectbox [data-baseweb="popover"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
    }

    .stSelectbox [role="option"] {
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
    }

    .stSelectbox [role="option"]:hover {
        background: rgba(59, 130, 246, 0.15) !important;
    }

    .stSelectbox [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.2) !important;
    }

    .stSelectbox svg {
        fill: var(--text-secondary) !important;
    }

    .stSelectbox [data-baseweb="icon"] {
        fill: var(--text-secondary) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus-within {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
    }

    .stButton > button {
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: var(--accent-blue) !important;
    }

    .stRadio > div {
        gap: 0.5rem;
    }

    .stRadio > div > label {
        background: rgba(0, 0, 0, 0.2);
        padding: 0.6rem 1.25rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--text-secondary);
    }

    .stRadio > div > label:has(input:checked) {
        background: rgba(59, 130, 246, 0.15);
        border-color: var(--accent-blue);
        color: var(--accent-blue);
    }

    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)) !important;
        border-radius: 10px !important;
    }

    .stProgress > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
    }

    .stCameraInput > div {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        background: rgba(0, 0, 0, 0.2) !important;
        padding: 0.5rem !important;
    }

    .stCameraInput video {
        border-radius: 10px !important;
        max-height: 140px !important;
        object-fit: cover !important;
    }

    .stCameraInput [data-testid="stCameraInputButton"] {
        padding: 0.5rem !important;
    }

    .stCameraInput [data-testid="stCameraInputButton"] button {
        padding: 0.4rem 0.75rem !important;
        font-size: 0.8rem !important;
    }

    .stAudioInput > div {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        background: rgba(0, 0, 0, 0.2) !important;
        padding: 0.75rem !important;
    }

    .stAudioInput [data-testid="stAudioInputButton"] button {
        padding: 0.4rem 0.75rem !important;
        font-size: 0.8rem !important;
    }

    .stAudioInput audio {
        max-height: 40px !important;
    }

    .stAudioInput > div {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        background: rgba(0, 0, 0, 0.2) !important;
        padding: 1rem !important;
    }

    .stFileUploader > div {
        background: rgba(0, 0, 0, 0.2);
        border: 2px dashed var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
    }

    .success-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 0.4rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
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

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(6, 182, 212, 0.15);
        color: #06b6d4;
        padding: 0.35rem 0.65rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
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

    .step-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent-blue);
    }

    .step-text {
        color: var(--text-muted);
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 1.5rem 0;
    }

    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.25rem;
        padding: 1rem 0;
    }

    .logo-container img {
        filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.4));
    }

    .logo-text h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 1px;
    }

    .logo-text p {
        margin: 0.15rem 0 0 0;
        color: var(--accent-cyan);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .question-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(6, 182, 212, 0.05) 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 14px;
        padding: 1.5rem;
    }

    .answer-area {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem;
    }

    .proctor-card {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 0.5rem;
        text-align: center;
    }

    .result-pass {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 182, 212, 0.15) 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }

    .result-fail {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.15) 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }

    @media (max-width: 1200px) {
        [data-testid="column"]:nth-child(3) { display: none; }
        .logo-container { flex-direction: column; text-align: center; gap: 0.75rem !important; }
    }

    @media (max-width: 992px) {
        .stApp { padding: 1rem !important; }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.35rem !important; }
        [data-testid="stHorizontalBlock"] { gap: 1rem !important; }
    }

    @media (max-width: 768px) {
        .stApp { padding: 0.75rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        .card { padding: 1.25rem !important; }
        
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 1rem !important;
        }
        
        .logo-container { flex-direction: column; gap: 0.5rem !important; }
        .logo-text h1 { font-size: 1.5rem !important; }
        
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        
        .question-card { padding: 1rem !important; }
        .question-card div { font-size: 1.1rem !important; }
        
        .stTextArea textarea { min-height: 120px !important; }
    }

    @media (max-width: 480px) {
        h1 { font-size: 1.25rem !important; }
        .card-title { font-size: 0.95rem !important; }
        
        .stButton > button {
            padding: 0.6rem 1rem !important;
            font-size: 0.85rem !important;
        }
        
        .success-badge, .error-badge, .info-badge, .live-badge {
            font-size: 0.65rem !important;
            padding: 0.3rem 0.5rem !important;
        }
        
        .proctor-card { padding: 0.5rem !important; }
        .result-pass, .result-fail { padding: 1rem !important; }
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        border: none !important;
    }

    .stAlert {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 10px !important;
    }

    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
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
                KILO_API_URL, 
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
else:
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
    st.session_state.interview_time = None
if 'mic_verified' not in st.session_state:
    st.session_state.mic_verified = False
if 'photo_verified' not in st.session_state:
    st.session_state.photo_verified = False

@st.dialog("Submit Interview?")
def confirm_submission():
    st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3 style="color: var(--text-primary) !important; -webkit-text-fill-color: var(--text-primary) !important;">Ready to Submit?</h3>
            <p style="color: var(--text-secondary);">Once submitted, you won't be able to modify your answers.</p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    if c1.button("✅ Submit Interview", use_container_width=True, type="primary"):
        with st.spinner("Processing your responses..."):
            st.session_state.step = 'report'
        st.rerun()
    if c2.button("❌ Continue Interviewing", use_container_width=True):
        st.rerun()

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
            <div style="display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 1.15rem; font-weight: 700; color: #f1f5f9; letter-spacing: 0.3px;">
                    {info['name'].upper()}
                </div>
                <div style="color: #64748b; font-size: 0.8rem; font-weight: 500; margin-top: 2px;">
                    ID: {info['id']} • {info['email']}
                </div>
                <div style="margin-top: 4px;">
                    <span class="success-badge">✓ IDENTITY VERIFIED</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        time_parts = st.session_state.interview_time.split(' ') if st.session_state.interview_time else ["", ""]
        st.markdown(f"""
            <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 4px;">
                <div style="color: #94a3b8; font-weight: 600; font-size: 0.9rem;">
                    📅 {time_parts[0]}
                </div>
                <div style="color: #64748b; font-size: 0.8rem;">
                    ⏱️ {time_parts[1]}
                </div>
                <span class="live-badge">● LIVE SESSION</span>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

def show_setup():
    st.markdown("""
        <div class="logo-container">
            <img src="data:image/png;base64,{LOGO_BASE64}" width="80">
            <div class="logo-text">
                <h1>MANVER <span style="color: #06b6d4;">AI INTERVIEWER</span></h1>
                <p>Advanced AI Interview Platform</p>
            </div>
        </div>
    """.format(LOGO_BASE64=LOGO_BASE64), unsafe_allow_html=True)
    
    st.markdown('<div style="height: 1px; background: linear-gradient(90deg, transparent, #3b82f6, transparent); margin: 0.5rem 0 2rem;"></div>', unsafe_allow_html=True)
    
    col_main, col_side = st.columns([1.3, 1], gap="large")
    
    with col_main:
        with st.container():
            st.markdown("""
                <div class="card-header">
                    <span class="card-icon">🔑</span>
                    <span class="card-title">Candidate Information</span>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                st.text_input("Full Name *", key="reg_name", placeholder="e.g. John Doe")
                st.text_input("Email ID *", key="reg_email", placeholder="john@example.com")
            with c2:
                st.text_input("Candidate ID *", key="reg_id", placeholder="e.g. CAND-001")
                st.text_input("Phone Number *", key="reg_phone", placeholder="+91 XXXX XXXX")
            
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
                uploaded_file = st.file_uploader("Upload Resume (PDF) *", type=['pdf'], label_visibility="collapsed")
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
                st.session_state.available_models,
                label_visibility="visible",
                help="Select the AI model to use for interview"
            )
            
            if st.button("🚀 Start Interview Session", type="primary", use_container_width=True):
                v_name = st.session_state.get("reg_name", "")
                v_id = st.session_state.get("reg_id", "")
                v_email = st.session_state.get("reg_email", "")
                v_phone = st.session_state.get("reg_phone", "")
                
                v_name = v_name.strip() if isinstance(v_name, str) else ""
                v_id = v_id.strip() if isinstance(v_id, str) else ""
                v_email = v_email.strip() if isinstance(v_email, str) else ""
                v_phone = str(v_phone).strip() if v_phone else ""
                
                if not v_name or not v_id or not v_email or not v_phone:
                    st.error("⚠️ All detail fields are mandatory.")
                elif input_type == "Upload Resume (PDF)" and not uploaded_file:
                    st.error("📄 Please upload your resume PDF.")
                elif input_type == "Paste Job Description (JD)" and not jd_text.strip():
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
                    st.session_state.interview_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    with st.spinner("Analyzing input and generating questions..."):
                        if input_type == "Upload Resume (PDF)":
                            input_content = extract_text_from_pdf(uploaded_file)
                            prompt_msg = "Analyze this resume and identify key skills, experience, and qualifications. Provide a detailed summary."
                        else:
                            input_content = jd_text
                            prompt_msg = "Analyze this job description and identify key skills, requirements, and qualifications needed. DO NOT INCLUDE ANY LINKS OR URLs."
                        
                        res = call_ai([{"role": "system", "content": prompt_msg}, {"role": "user", "content": input_content}], model=model)
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
                <div style="background: rgba(59, 130, 246, 0.08); padding: 0.75rem; border-radius: 10px; border: 1px solid rgba(59, 130, 246, 0.15); margin-bottom: 1rem;">
                    <div style="color: #60a5fa; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.5rem;">
                        🎤 Microphone Check
                    </div>
                    <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem;">
                        Record 1-2 seconds of audio to verify your microphone is working.
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            mic_test = st.audio_input("Test Microphone", key="mic_test_recording", label_visibility="collapsed")
            if mic_test:
                st.session_state.mic_verified = True
                st.markdown('<span class="success-badge">✓ Microphone Ready</span>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin: 1rem 0;"></div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div style="background: rgba(6, 182, 212, 0.08); padding: 0.75rem; border-radius: 10px; border: 1px solid rgba(6, 182, 212, 0.15); margin-bottom: 1rem;">
                    <div style="color: #06b6d4; font-weight: 600; font-size: 0.85rem; margin-bottom: 0.5rem;">
                        📸 Identity Verification
                    </div>
                    <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 0.5rem;">
                        Take a clear photo of yourself for identity verification.
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
                st.image(st.session_state.persistent_photo, width=140)
                st.markdown('<span class="success-badge">✓ Photo Captured</span>', unsafe_allow_html=True)

def show_analysis():
    render_header()
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <span class="info-badge">STEP 1 OF 3</span>
            <h1 style="margin-top: 0.75rem;">CANDIDATE INSIGHTS</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col_img, col_details = st.columns([1, 3], gap="large")
    
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
            st.markdown(f"""
                <div style="color: #cbd5e1; line-height: 1.7; font-size: 0.95rem;">
                    {st.session_state.analysis}
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("✅ Confirm & Proceed to Interview", type="primary", use_container_width=True):
            with st.spinner("Generating technical questionnaire..."):
                prompt = "Generate exactly 8 specific, high-level technical interview questions based on the provided skills. One question per line. No numbering. Make them challenging and relevant to the role."
                text = call_ai([{"role": "system", "content": prompt}, {"role": "user", "content": st.session_state.analysis}])
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
    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    col_qa, col_proc = st.columns([3, 1], gap="large")
    
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
        
        st.markdown('<div class="answer-area">', unsafe_allow_html=True)
        ans = st.text_area(
            "Your Answer", 
            value=st.session_state.answers[q_idx], 
            height=220, 
            key=f"ans_ta_{q_idx}", 
            placeholder="Type your answer here... You can use the voice input button below.",
            label_visibility="collapsed"
        )
        st.session_state.answers[q_idx] = ans
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_back, col_voice, col_next = st.columns([1, 1.2, 1.2], gap="medium")
        
        with col_back:
            if st.button("⬅️ Previous", disabled=(q_idx == 0), use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()
        
        with col_voice:
            st.markdown("""
                <button id="speak-btn" onclick="toggleSpeech()" style="
                    background: linear-gradient(135deg, #10b981, #059669); 
                    color: white; 
                    border: none; 
                    padding: 0.7rem 1rem; 
                    border-radius: 10px; 
                    width: 100%; 
                    cursor: pointer; 
                    font-weight: 600; 
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 0.5rem;
                    transition: all 0.2s;
                ">
                    🎤 Voice Input
                </button>
                <script>
                let recognition = null;
                let isListening = false;
                
                function toggleSpeech() {
                    if (!isListening) {
                        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        if (!SpeechRecognition) {
                            alert('Voice input not supported in this browser');
                            return;
                        }
                        recognition = new SpeechRecognition();
                        recognition.continuous = false;
                        recognition.interimResults = false;
                        recognition.lang = 'en-US';
                        
                        recognition.onstart = function() {
                            isListening = true;
                            document.getElementById('speak-btn').innerHTML = '🛑 Stop';
                            document.getElementById('speak-btn').style.background = '#ef4444';
                        };
                        
                        recognition.onresult = function(event) {
                            const transcript = event.results[0][0].transcript;
                            const textareas = window.parent.document.querySelectorAll('textarea');
                            for (let t of textareas) {
                                if (t && t.innerText !== undefined) {
                                    t.value = t.value ? t.value + ' ' + transcript : transcript;
                                    t.dispatchEvent(new Event('input', { bubbles: true }));
                                    break;
                                }
                            }
                        };
                        
                        recognition.onend = function() {
                            isListening = false;
                            document.getElementById('speak-btn').innerHTML = '🎤 Voice Input';
                            document.getElementById('speak-btn').style.background = 'linear-gradient(135deg, #10b981, #059669)';
                        };
                        
                        recognition.onerror = function() {
                            isListening = false;
                            document.getElementById('speak-btn').innerHTML = '🎤 Voice Input';
                            document.getElementById('speak-btn').style.background = 'linear-gradient(135deg, #10b981, #059669)';
                        };
                        
                        recognition.start();
                    }
                }
                </script>
            """, unsafe_allow_html=True)
        
        with col_next:
            label = "Finish Interview ✨" if q_idx + 1 == total else "Next Question ➡️"
            if st.button(label, use_container_width=True, type="primary"):
                if q_idx + 1 < total:
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    confirm_submission()
    
    with col_proc:
        st.markdown("""
            <div style="color: #64748b; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.75rem; letter-spacing: 0.5px;">
                📹 PROCTORING
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="proctor-card">', unsafe_allow_html=True)
        st.camera_input("Monitoring", key=f"proctor_cam_{q_idx}", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 0.5rem; border-radius: 8px; margin-top: 0.5rem; font-size: 0.65rem; font-weight: 600; text-align: center;">
                🛡️ LIVE MONITORING
            </div>
        """, unsafe_allow_html=True)

def show_interview():
    render_header()
    interview_content()

def show_report():
    info = st.session_state.user_info
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <span class="info-badge">FINAL RESULTS</span>
            <h1 style="margin-top: 0.5rem;">EVALUATION REPORT</h1>
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("AI is analyzing your interview performance..."):
        transcript = ""
        for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
            transcript += f"Q{i+1}: {q}\nA: {a}\n\n"
            
        res = call_ai([
            {"role": "system", "content": "You are an expert technical interviewer. Evaluate the candidate's interview responses. You MUST START your response with either 'RESULT: PASS' or 'RESULT: FAIL' based on the overall quality of answers, then provide detailed feedback including strengths, areas for improvement, and a final recommendation."},
            {"role": "user", "content": f"Candidate: {info.get('name', 'N/A')}\nID: {info.get('id', 'N/A')}\nEmail: {info.get('email', 'N/A')}\nDate: {st.session_state.interview_time}\n\nInterview Transcript:\n{transcript}"}
        ])
    
    is_pass = "PASS" in str(res).upper()
    
    col_result, col_candidate = st.columns([1.5, 1], gap="large")
    
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

if st.session_state.step == 'setup': 
    show_setup()
elif st.session_state.step == 'analysis': 
    show_analysis()
elif st.session_state.step == 'interview': 
    show_interview()
elif st.session_state.step == 'report': 
    show_report()
