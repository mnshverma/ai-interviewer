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

def show_loading_overlay(message="Loading..."):
    """Show a full-screen loading overlay"""
    st.markdown(f'''
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">{message}</p>
        </div>
    </div>
    <script>document.body.style.overflow = 'hidden';</script>
    ''', unsafe_allow_html=True)

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');

    :root {
        --bg-primary: #030712;
        --bg-glass: rgba(17, 24, 39, 0.7);
        --bg-card: rgba(31, 41, 55, 0.4);
        --accent-primary: #3b82f6;
        --accent-secondary: #8b5cf6;
        --gradient-main: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        --gradient-success: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        --gradient-error: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
        --text-primary: #f9fafb;
        --text-secondary: #9ca3af;
        --text-muted: #6b7280;
        --border-glass: rgba(255, 255, 255, 0.08);
        --shadow-premium: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
    }

    * {
        font-family: 'Inter', sans-serif !important;
        scroll-behavior: smooth;
    }

    .stApp {
        background: radial-gradient(circle at 0% 0%, #1e1b4b 0%, #030712 50%),
                    radial-gradient(circle at 100% 100%, #1e1b4b 0%, #030712 50%);
        background-attachment: fixed;
        min-height: 100vh;
    }

    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 820px !important;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.015em;
        margin: 0 !important;
    }

    h1 {
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        background: var(--gradient-main);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2 !important;
        animation: fadeInDown 0.8s ease-out;
    }

    .step-subtitle {
        color: var(--text-secondary);
        font-size: 1rem;
        margin-bottom: 2.5rem;
        animation: fadeIn 1s ease-out;
    }

    /* Wizards & Progress */
    .wizard-progress {
        display: flex;
        justify-content: center;
        gap: 0.75rem;
        margin-bottom: 2.5rem;
        padding: 1.25rem;
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: 20px;
        box-shadow: var(--shadow-premium);
        animation: fadeInUp 0.6s ease-out;
    }

    .wizard-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        min-width: 4rem;
        transition: transform 0.3s ease;
    }

    .wizard-step:hover {
        transform: translateY(-2px);
    }

    .wizard-step-num {
        width: 2.25rem;
        height: 2.25rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 700;
        border: 2px solid var(--border-glass);
        color: var(--text-muted);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(255, 255, 255, 0.03);
    }

    .wizard-step-num.active {
        border-color: transparent;
        color: white;
        background: var(--gradient-main);
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
        transform: scale(1.1);
    }

    .wizard-step-num.completed {
        border-color: transparent;
        color: white;
        background: var(--gradient-success);
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }

    .wizard-step-label {
        font-size: 0.65rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        transition: color 0.3s ease;
    }

    .wizard-step-label.active { color: var(--accent-primary); }
    .wizard-step-label.completed { color: #10b981; }

    /* Cards & Containers */
    .wizard-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-premium);
        animation: fadeIn 0.8s ease-out;
    }

    .wizard-card-center { text-align: center; }

    /* Inputs Overhaul */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 14px !important;
        color: white !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-primary) !important;
        background: rgba(0, 0, 0, 0.3) !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15) !important;
    }

    /* Buttons Overhaul */
    .stButton > button {
        border-radius: 14px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
        text-transform: none !important;
    }

    .stButton > button[type="primary"] {
        background: var(--gradient-main) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }

    .stButton > button[type="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
    }

    .stButton > button[type="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--text-primary) !important;
        backdrop-filter: blur(8px);
        border: 1px solid var(--border-glass) !important;
    }

    .stButton > button[type="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }

    /* Data Visualization */
    .stProgress > div > div > div {
        background: var(--gradient-success) !important;
        height: 8px !important;
        border-radius: 10px !important;
    }

    /* Animations */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb {
        background: var(--border-glass);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* Responsive Scaling */
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; }
        h1 { font-size: 1.75rem !important; }
        .wizard-progress { padding: 0.75rem; gap: 0.4rem; }
        .wizard-step { min-width: 3rem; }
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
    st.session_state.step = 'device_test'

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

@st.dialog("Confirm Submission")
def confirm_submission():
    if st.session_state.get('submitting_interview', False):
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div class="loading-spinner" style="width: 50px; height: 50px; margin: 0 auto 1.5rem;"></div>
                <h3 style="margin-bottom: 0.5rem;">Finalizing Assessment</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem;">AI is evaluating your session. Please hold on.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
            <h2 style="margin-bottom: 1rem;">Ready to finish?</h2>
            <p style="color: var(--text-secondary); line-height: 1.6;">Once submitted, your responses will be processed and cannot be edited. A final score and report will be generated.</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        if st.button("✅ Yes, Submit", use_container_width=True, type="primary"):
            st.session_state.submitting_interview = True
            st.session_state.step = 'report'
            st.rerun()
    with c2:
        if st.button("🔙 Not yet", use_container_width=True, type="secondary"):
            st.rerun()

def render_branding():
    """Ultra-premium branding header"""
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 3rem;">
            <div style="display: inline-flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 1.5rem 2.5rem; background: var(--bg-glass); border-radius: 32px; border: 1px solid var(--border-glass); box-shadow: var(--shadow-premium); backdrop-filter: blur(20px); animation: fadeIn 1s ease-out;">
                <div style="width: 80px; height: 80px; background: rgba(0,0,0,0.2); border-radius: 20px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--border-glass); margin-bottom: 0.5rem;">
                    <img src="data:image/png;base64,{LOGO_BASE64}" style="height: 50px; filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.4));">
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; background: var(--gradient-main); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 0.15em; text-transform: uppercase;">
                    MANVER AI
                </div>
                <div style="color: var(--text-muted); font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2em; text-transform: uppercase; opacity: 0.8;">
                    Next-Gen Candidate Screening
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_step_progress():
    """Render a clean wizard-style progress indicator"""
    steps = [
        {"label": "Verify", "step": "device_test"},
        {"label": "Photo", "step": "photo_capture"},
        {"label": "Sync", "step": "eye_calibration"},
        {"label": "Details", "step": "setup"},
        {"label": "Analyze", "step": "analysis"},
        {"label": "Session", "step": "interview"},
        {"label": "Results", "step": "report"}
    ]

    current_step = st.session_state.get('step', 'device_test')
    current_idx = 0
    for i, s in enumerate(steps):
        if s['step'] == current_step:
            current_idx = i
            break

    html = '<div class="wizard-progress">'

    for i, s in enumerate(steps):
        if i < current_idx:
            num_class = "completed"
            label_class = "completed"
            num_content = "✓"
        elif i == current_idx:
            num_class = "active"
            label_class = "active"
            num_content = str(i + 1)
        else:
            num_class = ""
            label_class = ""
            num_content = str(i + 1)

        html += f'''
            <div class="wizard-step">
                <div class="wizard-step-num {num_class}">{num_content}</div>
                <div class="wizard-step-label {label_class}">{s['label']}</div>
            </div>
        '''

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_header():
    """Minimal header - only shows during interview and report"""
    if 'user_info' not in st.session_state or not st.session_state.user_info.get("name"):
        return

    step = st.session_state.get('step', 'device_test')
    if step not in ['interview', 'report']:
        return

    info = st.session_state.user_info
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: var(--bg-glass); backdrop-filter: blur(8px); border: 1px solid var(--border-glass); border-radius: 16px; margin-bottom: 2rem; box-shadow: var(--shadow-premium);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 32px; height: 32px; background: var(--gradient-main); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: white; font-size: 0.8rem;">
                    {info['name'][0].upper() if info['name'] else 'C'}
                </div>
                <div>
                    <div style="font-weight: 700; color: var(--text-primary); font-size: 0.9rem; line-height: 1;">
                        {info['name']}
                    </div>
                    <div style="color: var(--text-muted); font-size: 0.65rem; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px;">
                        {info['id']}
                    </div>
                </div>
            </div>
            <div style="color: var(--text-muted); font-size: 0.75rem; font-weight: 500;">
                {st.session_state.interview_time}
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_device_test():
    render_branding()
    render_step_progress()
    st.markdown("""
        <div style="text-align: center; margin-top: 1rem;">
            <h1>Ready to Begin?</h1>
            <p class="step-subtitle" style="margin-top: 0.5rem;">Join thousands of candidates worldwide in our secure assessment environment.</p>
        </div>
    """, unsafe_allow_html=True)

    step_num = st.session_state.get("device_test_step", 0)

    if step_num == 0:
        st.markdown("""
            <div class="wizard-card wizard-card-center" style="padding: 3rem 2rem;">
                <div style="font-size: 4rem; margin-bottom: 2rem; animation: pulse 2.5s infinite;">🛡️</div>
                <h2 style="margin-bottom: 1.25rem; font-size: 2rem !important;">Advanced Session Shield</h2>
                <p style="color: var(--text-secondary); max-width: 500px; margin: 0 auto 2.5rem; line-height: 1.8; font-size: 1.05rem;">
                    To initiate your secure interview, we must verify your system's hardware configuration. 
                    This ensures optimal video and audio transmission during your session.
                </p>
                <div style="display: flex; justify-content: center; gap: 2rem; color: var(--text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">
                    <span style="display: flex; align-items: center; gap: 0.5rem;">🔒 Encrypted</span>
                    <span style="display: flex; align-items: center; gap: 0.5rem;">⚡ Low Latency</span>
                    <span style="display: flex; align-items: center; gap: 0.5rem;">🤖 AI Powered</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Start System Initialization", type="primary", use_container_width=True):
            st.session_state.device_test_step = 1
            st.rerun()

    elif step_num == 1:
        st.markdown("""
            <div style="margin-top: 1rem; margin-bottom: 2rem;">
                <h3 style="margin-bottom: 0.5rem;">Hardware Configuration</h3>
                <p style="color: var(--text-secondary); font-size: 0.95rem;">Test your inputs before proceeding to the session</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown('<div class="wizard-card" style="padding: 1.5rem; height: 100%;">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-bottom: 1.25rem;">📷 Video Status</h4>', unsafe_allow_html=True)
            camera_ok = st.camera_input("Test camera", label_visibility="collapsed", key="test_camera")
            if camera_ok:
                st.markdown('<div style="margin-top: 1rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: 10px; border: 1px solid rgba(16, 185, 129, 0.2);"><p style="color: #10b981; margin: 0; font-weight: 600; text-align: center; font-size: 0.85rem;">✓ Video Ready</p></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="wizard-card" style="padding: 1.5rem; height: 100%;">', unsafe_allow_html=True)
            st.markdown('<h4 style="margin-bottom: 1.25rem;">🎤 Audio Status</h4>', unsafe_allow_html=True)
            mic_ok = st.audio_input("Test microphone", label_visibility="collapsed", key="test_mic")
            if mic_ok:
                st.markdown('<div style="margin-top: 1rem; padding: 0.75rem; background: rgba(16, 185, 129, 0.1); border-radius: 10px; border: 1px solid rgba(16, 185, 129, 0.2);"><p style="color: #10b981; margin: 0; font-weight: 600; text-align: center; font-size: 0.85rem;">✓ Audio Detected</p></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)
        col_back, _, col_next = st.columns([1, 0.2, 1])
        with col_back:
            if st.button("← Reset Defaults", use_container_width=True, type="secondary"):
                st.session_state.device_test_step = 0
                st.rerun()
        with col_next:
            can_proceed = camera_ok is not None and mic_ok is not None
            if st.button("Finalize Verification →", type="primary", use_container_width=True, disabled=not can_proceed):
                st.session_state.device_test_done = True
                st.session_state.device_permissions_granted = True
                st.session_state.photo_verified = True
                st.session_state.mic_verified = True
                st.session_state.persistent_photo = camera_ok
                st.session_state.step = 'photo_capture'
                st.rerun()

def show_photo_capture():
    render_branding()
    render_step_progress()
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1>Identification</h1>
            <p style="color: var(--text-secondary);">Verify your identity for the official session record</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_cam, col_info = st.columns([1.2, 1], gap="large")
    
    with col_cam:
        st.markdown('<div class="wizard-card" style="padding: 1.25rem;">', unsafe_allow_html=True)
        photo_cam = st.camera_input(
            "Capture Identity", 
            key="photo_capture_cam",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if photo_cam:
            st.session_state.persistent_photo = photo_cam
            st.session_state.photo_verified = True
            st.markdown('<div style="text-align: center; color: #10b981; font-weight: 600; margin-top: 1rem;">✨ Verification Photo Captured</div>', unsafe_allow_html=True)
    
    with col_info:
        st.markdown("""
            <div class="wizard-card">
                <h3 style="margin-bottom: 1.25rem;">Guidelines</h3>
                <div style="display: grid; gap: 0.75rem; color: var(--text-secondary); font-size: 0.9rem;">
                    <div style="display: flex; gap: 0.75rem;"><span>👤</span> Clear face visibility</div>
                    <div style="display: flex; gap: 0.75rem;"><span>💡</span> Good ambient lighting</div>
                    <div style="display: flex; gap: 0.75rem;"><span>👓</span> No sunglasses/hats</div>
                    <div style="display: flex; gap: 0.75rem;"><span>🎯</span> Look directly forward</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("photo_verified") and st.button("Finalize Verification →", type="primary", use_container_width=True):
            st.session_state.mic_verified = True
            st.session_state.device_test_done = True
            st.session_state.device_permissions_granted = True
            st.session_state.step = 'eye_calibration'
            st.rerun()
        
        if st.button("← Go Back", use_container_width=True):
            st.session_state.step = 'device_test'
            st.rerun()

def show_eye_calibration():
    render_branding()
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
            <div class="wizard-card">
                <h3 style="margin-bottom: 1.25rem;">Calibration Protocol</h3>
                <div style="display: grid; gap: 1rem; color: var(--text-secondary); font-size: 0.9rem;">
                    <div style="display: flex; gap: 0.75rem;"><span>📏</span> Maintain arm's length distance</div>
                    <div style="display: flex; gap: 0.75rem;"><span>👁️</span> Focus directly on the camera</div>
                    <div style="display: flex; gap: 0.75rem;"><span>🧘</span> Remain stationary for 3 seconds</div>
                </div>
                <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(59, 130, 246, 0.08); border-radius: 14px; border: 1px solid rgba(59, 130, 246, 0.15);">
                    <p style="color: var(--accent-primary); font-size: 0.8rem; line-height: 1.5; margin: 0;">
                        <b>Security Note:</b> Gaze monitoring is active during the session. Persistent looking away may trigger automated warnings.
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
    render_branding()
    render_step_progress()

    st.markdown("<h1>Your Details</h1>", unsafe_allow_html=True)
    st.markdown('<p class="step-subtitle">Tell us about yourself to get started</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.text_input("Full Name *", key="reg_name", placeholder="e.g. John Doe")
        st.text_input("Email ID *", key="reg_email", placeholder="john@example.com")
    with c2:
        st.text_input("Candidate ID *", key="reg_id", placeholder="e.g. CAND-001")
        st.text_input("Phone Number *", key="reg_phone", placeholder="+91 XXXX XXXX")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### Resume or Job Description")
    input_type = st.radio(
        "Choose input type:",
        ["Upload Resume (PDF)", "Paste Job Description"],
        horizontal=True,
        label_visibility="collapsed"
    )

    uploaded_file = None
    jd_text = ""

    if input_type == "Upload Resume (PDF)":
        uploaded_file = st.file_uploader("Upload Resume", type=['pdf'], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"✓ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    else:
        jd_text = st.text_area("Job Description", height=150, placeholder="Paste the job description here...", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, _, col3 = st.columns([1, 0.5, 1], gap="medium")
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 'device_test'
            st.rerun()
    with col3:
        if st.button("Continue →", type="primary", use_container_width=True):
            v_name = str(st.session_state.get("reg_name", "")).strip()
            v_id = str(st.session_state.get("reg_id", "")).strip()
            v_email = str(st.session_state.get("reg_email", "")).strip()
            v_phone = str(st.session_state.get("reg_phone", "")).strip()

            missing = []
            if not v_name: missing.append("Name")
            if not v_email: missing.append("Email")
            if not v_id: missing.append("ID")
            if not v_phone: missing.append("Phone")

            if missing:
                st.error(f"Please fill: {', '.join(missing)}")
            elif input_type == "Upload Resume (PDF)" and not uploaded_file:
                st.error("Please upload your resume")
            elif input_type == "Paste Job Description" and not jd_text.strip():
                st.error("Please paste the job description")
            else:
                st.session_state.user_info = {
                    "name": v_name, "id": v_id,
                    "email": v_email, "phone": v_phone
                }
                st.session_state.interview_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

                show_loading_overlay("Analyzing your information...")

                if input_type == "Upload Resume (PDF)":
                    input_content = extract_text_from_pdf(uploaded_file)
                    prompt_msg = "Analyze this resume and identify key skills, experience, and qualifications. Provide a detailed summary."
                else:
                    input_content = jd_text
                    prompt_msg = "Analyze this job description and identify key skills, requirements, and qualifications needed. DO NOT INCLUDE ANY LINKS OR URLs."

                model = st.session_state.get("available_models", ["kilo-auto/free"])[0]
                res = safe_api_call(call_ai, [{"role": "system", "content": prompt_msg}, {"role": "user", "content": input_content}], model=model)
                
                hide_loading_overlay() # Added hide
                
                if res:
                    st.session_state.analysis = res
                    st.session_state.step = 'analysis'
                    st.rerun()

def show_analysis():
    render_branding()
    render_step_progress()

    st.markdown("<h1>Analysis</h1>", unsafe_allow_html=True)
    st.markdown('<p class="step-subtitle">Review your profile analysis before proceeding</p>', unsafe_allow_html=True)

    info = st.session_state.user_info
    st.markdown(f"""
        <div class="wizard-card">
            <h3 style="margin-bottom: 1rem; color: var(--text-primary);">Your Profile</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; color: var(--text-secondary); font-size: 0.9rem;">
                <div><strong style="color: var(--text-primary);">Name:</strong> {info['name']}</div>
                <div><strong style="color: var(--text-primary);">ID:</strong> {info['id']}</div>
                <div><strong style="color: var(--text-primary);">Email:</strong> {info['email']}</div>
                <div><strong style="color: var(--text-primary);">Phone:</strong> {info['phone']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    analysis_text = st.session_state.get('analysis', '').strip()
    if analysis_text:
        with st.expander("View AI Analysis Summary", expanded=False):
            st.markdown(analysis_text)
    else:
        st.warning("Analysis data is not available. Please go back and try again.")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, _, col3 = st.columns([1, 0.5, 1], gap="medium")
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 'setup'
            st.rerun()
    with col3:
        if not analysis_text:
            st.button("Continue →", type="primary", use_container_width=True, disabled=True)
        elif st.button("Continue →", type="primary", use_container_width=True):
            show_loading_overlay("Preparing your interview...")

            prompt = "Generate exactly 8 specific, high-level technical interview questions based on the provided skills. One question per line. No numbering. Make them challenging and relevant to the role."
            text = safe_api_call(call_ai, [{"role": "system", "content": prompt}, {"role": "user", "content": analysis_text}])
            
            hide_loading_overlay() # Added hide
            
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
                st.warning("Please keep your eyes on the screen. First warning.")
            elif strike_num == 2:
                st.error("Warning: Looking away is considered cheating. One more and you may be terminated.")
            elif strike_num == 3:
                st.error("Final warning. Look away again and your interview will be terminated.")
            elif strike_num >= 4:
                st.session_state.interview_terminated = True
                tracker.state.is_active = False
                st.markdown("""
                    <div class="termination-screen">
                        <div style="font-size: 4rem;">❌</div>
                        <h1 style="color: var(--accent-red); font-size: 2rem; margin-top: 1rem;">Interview Terminated</h1>
                        <p style="color: var(--text-secondary); margin-top: 1rem;">Repeated eye-tracking violations detected.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.session_state.step = 'report'
                st.rerun()

    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)

    # Question header
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1rem;">
            <h2 style="margin: 0;">Question {q_idx + 1}</h2>
            <span style="color: var(--text-muted); font-size: 0.85rem; font-weight: 600;">{q_idx + 1} / {total}</span>
        </div>
    """, unsafe_allow_html=True)
    st.progress((q_idx + 1) / total)

    st.markdown(f"""
        <div class="wizard-card" style="margin-top: 1.5rem; border-left: 4px solid var(--accent-primary);">
            <div style="font-size: 1.15rem; font-weight: 500; color: var(--text-primary); line-height: 1.6;">
                {st.session_state.questions[q_idx]}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.answers[q_idx] = st.text_area(
        "Response Area",
        value=st.session_state.answers[q_idx],
        height=220,
        key=f"ans_ta_{q_idx}",
        placeholder="Type your comprehensive response here...",
        label_visibility="collapsed"
    )

    col_back, _, col_next = st.columns([1, 0.4, 1], gap="medium")

    with col_back:
        if st.button("← Previous Question", disabled=(q_idx == 0), use_container_width=True, type="secondary"):
            st.session_state.current_q -= 1
            st.rerun()

    with col_next:
        label = "Complete Interview" if q_idx + 1 == total else "Next Question →"
        if st.button(label, use_container_width=True, type="primary"):
            if q_idx + 1 < total:
                st.session_state.current_q += 1
                st.rerun()
            else:
                confirm_submission()

    # Proctoring section (Refined)
    with st.expander("🛠️ Advanced Monitoring & AI Assistant", expanded=False):
        t_col1, t_col2 = st.columns([1, 1.2])
        with t_col1:
            st.markdown("##### 📹 Vision Status")
            proctor_frame = st.camera_input("Camera", key="interview_camera", label_visibility="collapsed")
            
            if proctor_frame is not None and tracker and st.session_state.get('eye_tracking_active'):
                import cv2
                import numpy as np
                bytes_data = proctor_frame.getvalue()
                frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                tracker.process_frame(frame)
        
        with t_col2:
            st.markdown("##### 📊 Integrity Report")
            tracker = st.session_state.get('eye_tracker')
            strikes = tracker.state.strikes if tracker else 0
            
            if strikes > 0:
                st.warning(f"Attention Required: {strikes} tracking anomalies detected.")
            else:
                st.markdown('<div style="padding: 15px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2);"><p style="color: #10b981; margin: 0; font-weight: 600;">✅ Tracking: Secure & Compliant</p></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<p style="color: var(--text-muted); font-size: 0.8rem;">Session ID: {st.session_state.user_info.get("id", "N/A")}</p>', unsafe_allow_html=True)

def show_interview():
    render_step_progress()
    interview_content()

def show_report():
    render_step_progress()

    info = st.session_state.user_info

    show_loading_overlay("Evaluating your performance...")

    transcript = ""
    for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
        transcript += f"Q{i+1}: {q}\nA: {a}\n\n"

    res = safe_api_call(call_ai, [
        {"role": "system", "content": "You are an expert technical interviewer. Evaluate the candidate's interview responses. You MUST START your response with either 'RESULT: PASS' or 'RESULT: FAIL' based on the overall quality of answers, then provide detailed feedback including strengths, areas for improvement, and a final recommendation."},
        {"role": "user", "content": f"Candidate: {info.get('name', 'N/A')}\nID: {info.get('id', 'N/A')}\nEmail: {info.get('email', 'N/A')}\nDate: {st.session_state.interview_time}\n\nInterview Transcript:\n{transcript}"}
    ])

    hide_loading_overlay() # Added hide

    is_pass = "PASS" in str(res).upper()

    st.markdown("<h1>Performance Report</h1>", unsafe_allow_html=True)

    # Result state card
    if is_pass:
        st.markdown(f"""
            <div class="wizard-card" style="border-left: 5px solid #10b981; background: rgba(16, 185, 129, 0.05);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2.5rem;">🎉</span>
                    <div>
                        <h3 style="margin: 0; color: #10b981 !important;">Interview Successful</h3>
                        <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">You have met the technical threshold for this assessment.</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="wizard-card" style="border-left: 5px solid #ef4444; background: rgba(239, 68, 68, 0.05);">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2.5rem;">📋</span>
                    <div>
                        <h3 style="margin: 0; color: #ef4444 !important;">Session Completed</h3>
                        <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">The assessment is complete. Review your feedback below.</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Main evaluation logic
    if res:
        analysis_text = res.replace("RESULT: PASS", "").replace("RESULT: FAIL", "").strip()
        st.markdown("### AI Evaluation & Feedback")
        st.markdown(f"""
            <div class="wizard-card" style="line-height: 1.7; color: var(--text-secondary);">
                {analysis_text}
            </div>
        """, unsafe_allow_html=True)
    
    # Metrics row
    tracker = st.session_state.get('eye_tracker')
    if tracker and st.session_state.get('eye_tracking_active'):
        report = tracker.generate_report()
        score = report.get('compliance_score', 0)
        strikes = report.get('strikes', 0)
        
        # Duration calculation
        try:
            start_dt = datetime.strptime(st.session_state.interview_time, "%B %d, %Y at %I:%M %p")
            duration_mins = int((datetime.now() - start_dt).total_seconds() / 60)
            duration_str = f"{duration_mins}m" if duration_mins > 0 else "< 1m"
        except:
            duration_str = "N/A"
            
        st.markdown("### Integrity & Compliance")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
                <div class="wizard-card" style="text-align: center; padding: 1.25rem;">
                    <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem;">Compliance</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: var(--accent-primary);">{score:.0f}%</div>
                </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div class="wizard-card" style="text-align: center; padding: 1.25rem;">
                    <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem;">Alerts</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: { '#ef4444' if strikes > 0 else '#10b981' };">{strikes}/4</div>
                </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
                <div class="wizard-card" style="text-align: center; padding: 1.25rem;">
                    <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem;">Duration</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: var(--text-primary);">{duration_str}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_pdf, col_new = st.columns(2, gap="medium")
    with col_pdf:
        pdf_data = create_pdf_report(info, res, transcript, st.session_state.get('persistent_photo'))
        st.download_button(
            label="📄 Download Official Report",
            data=pdf_data,
            file_name=f"Assessment_{info.get('name', 'Report')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    with col_new:
        if st.button("Start New Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

step = st.session_state.get('step', 'device_test')

# Only show session header if user is identified
if step in ['interview', 'report'] and st.session_state.get('user_info'):
     render_header()

if step == 'device_test':
    show_device_test()
elif step == 'photo_capture':
    show_photo_capture()
elif step == 'eye_calibration':
    show_eye_calibration()
elif step == 'setup':
    show_setup()
elif step == 'analysis':
    show_analysis()
elif step == 'interview':
    show_interview()
elif step == 'report':
    show_report()
