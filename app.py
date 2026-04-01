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

def show_loading_overlay(message="Loading..."):
    """Show a full-screen loading overlay"""
    st.markdown(f'''
    <div class="loading-overlay">
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

    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2332;
        --accent-blue: #3b82f6;
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
        min-height: 100vh;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 2rem !important;
        max-width: 700px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        margin: 0 auto;
    }

    header[data-testid="stHeader"],
    [data-testid="stFooter"],
    [data-testid="stMainBlockMenu"],
    #MainMenu, footer, header {
        display: none !important;
        visibility: hidden !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }

    h1 {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.25rem !important;
    }

    h2 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }

    .step-subtitle {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    /* Progress Bar */
    .wizard-progress {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
        padding: 1rem;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
    }

    .wizard-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.35rem;
        min-width: 3.5rem;
    }

    .wizard-step-num {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        border: 2px solid var(--border-color);
        color: var(--text-muted);
        background: transparent;
    }

    .wizard-step-num.active {
        border-color: var(--accent-blue);
        color: white;
        background: var(--accent-blue);
    }

    .wizard-step-num.completed {
        border-color: var(--accent-green);
        color: white;
        background: var(--accent-green);
    }

    .wizard-step-label {
        font-size: 0.6rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .wizard-step-label.active {
        color: var(--accent-blue);
    }

    .wizard-step-label.completed {
        color: var(--accent-green);
    }

    /* Cards */
    .wizard-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .wizard-card-center {
        text-align: center;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        background: rgba(0,0,0,0.2) !important;
        color: var(--text-primary) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-blue) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
    }

    .stTextInput label, .stTextArea label {
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        color: var(--text-secondary) !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        padding: 0.65rem 1.25rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--accent-blue) !important;
        color: white !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #2563eb !important;
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.05) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* File Upload */
    .stFileUploader {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        background: rgba(0,0,0,0.1) !important;
    }

    .stFileUploader:hover {
        border-color: var(--accent-blue) !important;
    }

    /* Progress Bar in Interview */
    .stProgress > div > div > div {
        background: var(--accent-green) !important;
    }

    /* Alert Messages */
    .stAlert {
        border-radius: 8px !important;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        .wizard-step {
            min-width: 2.5rem;
        }

        .wizard-step-label {
            font-size: 0.5rem;
        }
    }

    @media (max-width: 480px) {
        h1 {
            font-size: 1.5rem !important;
        }

        .wizard-step-label {
            display: none;
        }
    }

    /* Loading Overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(10, 14, 23, 0.95);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .loading-content {
        text-align: center;
    }

    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid rgba(255,255,255,0.1);
        border-top-color: var(--accent-blue);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Camera Input */
    .stCameraInput video {
        border-radius: 12px !important;
    }

    /* Warning Modal */
    .warning-overlay {
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
        text-align: center;
    }

    /* Termination */
    .termination-screen {
        background: var(--bg-primary);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem;
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
    """Render a clean wizard-style progress indicator"""
    steps = [
        {"label": "Setup", "step": "device_test"},
        {"label": "Details", "step": "setup"},
        {"label": "Analysis", "step": "analysis"},
        {"label": "Interview", "step": "interview"},
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
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border-color); margin-bottom: 1rem;">
            <div style="font-weight: 600; color: var(--text-primary); font-size: 0.9rem;">
                {info['name']}
            </div>
            <div style="color: var(--text-muted); font-size: 0.75rem;">
                {info['id']} | {st.session_state.interview_time}
            </div>
        </div>
    """, unsafe_allow_html=True)

def show_device_test():
    render_step_progress()

    st.markdown("<h1>Setup Your Devices</h1>", unsafe_allow_html=True)
    st.markdown('<p class="step-subtitle">Allow camera and microphone access to continue</p>', unsafe_allow_html=True)

    step = st.session_state.get("device_test_step", 0)

    if step == 0:
        st.markdown("""
            <div class="wizard-card wizard-card-center">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">📷🎤</div>
                <h3 style="color: var(--text-primary) !important; margin-bottom: 0.75rem;">Device Permissions Required</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; max-width: 400px; margin: 0 auto;">
                    We need access to your camera and microphone for the video interview.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Enable Camera & Microphone", type="primary", use_container_width=True):
            st.session_state.device_test_step = 1
            st.rerun()

    elif step == 1:
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("#### 📷 Camera")
            camera_ok = st.camera_input("Test camera", label_visibility="collapsed", key="test_camera")
            if camera_ok:
                st.success("Camera working!")

        with col2:
            st.markdown("#### 🎤 Microphone")
            mic_ok = st.audio_input("Test microphone", label_visibility="collapsed", key="test_mic")
            if mic_ok:
                st.success("Microphone working!")

        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.device_test_step = 0
                st.rerun()
        with col2:
            can_proceed = camera_ok is not None and mic_ok is not None
            if st.button("Continue →", type="primary", use_container_width=True, disabled=not can_proceed):
                st.session_state.device_test_done = True
                st.session_state.device_permissions_granted = True
                st.session_state.photo_verified = True
                st.session_state.mic_verified = True
                st.session_state.persistent_photo = camera_ok
                st.session_state.step = 'setup'
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
    render_header()
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
                if res:
                    st.session_state.analysis = res
                    st.session_state.step = 'analysis'
                    st.rerun()

def show_analysis():
    render_header()
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

    # Question and answer area
    st.progress((q_idx + 1) / total, text=f"Question {q_idx + 1} of {total}")

    st.markdown(f"""
        <div class="wizard-card" style="margin-bottom: 1rem;">
            <div style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary); line-height: 1.6;">
                {st.session_state.questions[q_idx]}
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.session_state.answers[q_idx] = st.text_area(
        "Your Answer",
        value=st.session_state.answers[q_idx],
        height=180,
        key=f"ans_ta_{q_idx}",
        placeholder="Type your answer here...",
        label_visibility="collapsed"
    )

    col_back, _, col_next = st.columns([1, 0.5, 1], gap="medium")

    with col_back:
        if st.button("← Previous", disabled=(q_idx == 0), use_container_width=True):
            st.session_state.current_q -= 1
            st.rerun()

    with col_next:
        label = "Finish" if q_idx + 1 == total else "Next →"
        if st.button(label, use_container_width=True, type="primary"):
            if q_idx + 1 < total:
                st.session_state.current_q += 1
                st.rerun()
            else:
                confirm_submission()

    # Proctoring section (collapsible)
    with st.expander("📹 Monitoring", expanded=False):
        tracker = st.session_state.get('eye_tracker')
        strikes = tracker.state.strikes if tracker else 0

        camera_key = "interview_camera"
        proctor_frame = st.camera_input("Camera", key=camera_key, label_visibility="collapsed")

        if proctor_frame is not None and tracker and st.session_state.get('eye_tracking_active'):
            import cv2
            import numpy as np
            bytes_data = proctor_frame.getvalue()
            frame = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            gaze_result = tracker.process_frame(frame)

        if strikes > 0:
            st.error(f"Strikes: {strikes}/4")
        else:
            st.success("Status: Compliant")

def show_interview():
    render_header()
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

    is_pass = "PASS" in str(res).upper()

    st.markdown("<h1>Results</h1>", unsafe_allow_html=True)

    # Result card
    if is_pass:
        st.success("PASS - Congratulations! You successfully completed the interview.")
    else:
        st.error("FAIL - Thank you for your time. We encourage you to apply again.")

    # Candidate info
    st.markdown(f"""
        <div class="wizard-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary);">{info.get('name', 'N/A')}</div>
                    <div style="color: var(--text-muted); font-size: 0.85rem;">{info.get('id', 'N/A')} | {info.get('email', 'N/A')}</div>
                </div>
                <div style="color: var(--text-muted); font-size: 0.85rem;">{st.session_state.interview_time}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Analysis
    if res:
        analysis_text = res.replace("RESULT: PASS", "").replace("RESULT: FAIL", "").strip()
        with st.expander("View Detailed Analysis", expanded=True):
            st.markdown(analysis_text)
    else:
        st.info("Interview completed. Your responses have been recorded.")

    # Transcript
    with st.expander("View Interview Transcript", expanded=False):
        for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"**A:** {a if a else '_No answer provided_'}")
            if i < len(st.session_state.questions) - 1:
                st.markdown("---")

    # Eye tracking report
    tracker = st.session_state.get('eye_tracker')
    if tracker and st.session_state.get('eye_tracking_active'):
        report = tracker.generate_report()
        st.session_state.eye_tracking_report = report

        with st.expander("Eye Tracking Report", expanded=False):
            score = report.get('compliance_score', 0)
            strikes = report.get('strikes', 0)
            total_events = report.get('total_events', 0)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Compliance", f"{score:.0f}%")
            with col2:
                st.metric("Warnings", f"{strikes}/4")
            with col3:
                st.metric("Gaze Events", str(total_events))

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Start New Interview", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

step = st.session_state.get('step', 'device_test')

if step == 'device_test':
    show_device_test()
elif step == 'setup':
    show_setup()
elif step == 'analysis':
    show_analysis()
elif step == 'interview':
    show_interview()
elif step == 'report':
    show_report()
