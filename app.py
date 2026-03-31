import streamlit as st
import os
import requests
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import time
from fpdf import FPDF
from datetime import datetime

# --- Setup ---
load_dotenv()
LOGO_PATH = "manver-logo.png"
import base64
with open(LOGO_PATH, "rb") as f: LOGO_BASE64 = base64.b64encode(f.read()).decode()
st.set_page_config(page_title="MANVER AI INTERVIEWER", page_icon=LOGO_PATH, layout="wide")

# --- Configuration ---
KILO_API_URL = "https://api.kilo.ai/api/gateway/chat/completions"
DEFAULT_MODEL = "kilo-auto/free"

# --- Global Header ---
def render_header():
    if 'user_info' not in st.session_state or not st.session_state.user_info.get("name"): return
    
    st.markdown('<div class="glass-card" style="margin-bottom: 2rem; padding: 0.8rem; border-left: 5px solid #3b82f6;">', unsafe_allow_html=True)
    h_c1, h_c2, h_c3, h_c4 = st.columns([1, 1, 4, 3], gap="small")
    
    with h_c1:
        st.image(LOGO_PATH, width=70) # Slightly smaller
        
    with h_c2:
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, width=75) # Slightly smaller
            
    with h_c3:
        info = st.session_state.user_info
        st.markdown(f"""
            <div style="padding-top: 0px;">
                <h3 style="margin:0; color:#eff6ff; text-transform: uppercase; font-size: 1.2rem; letter-spacing: 0.5px;">{info['name']}</h3>
                <div style="margin:0; color:#60a5fa; font-family:monospace; font-weight:700; font-size: 0.85rem;">ID: {info['id']}</div>
                <div style="margin-top:4px; font-size:0.65rem; color:#10b981; font-weight:600; letter-spacing: 1px;">🛡️ IDENTITY VERIFIED</div>
            </div>
        """, unsafe_allow_html=True)
        
    with h_c4:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 0px;">
                <div style="color: #60a5fa; font-weight: 700; font-size: 0.9rem; margin-bottom: 2px;">📅 {st.session_state.interview_time.split(' ')[0]}</div>
                <div style="color: #94a3b8; font-weight: 600; font-size: 0.8rem;">⏱️ {st.session_state.interview_time.split(' ')[1]}</div>
                <div style="margin-top: 5px; font-size: 0.6rem; color: #4ade80; border: 1px solid #10b981; padding: 2px 8px; border-radius: 20px; display: inline-block;">📡 LIVE</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PDF Generator ---
def create_pdf_report(info, evaluation, transcript, photo_bytes=None):
    pdf = FPDF()
    pdf.add_page()
    
    is_pass = "PASS" in str(evaluation).upper()
    decision_color = (16, 185, 129) if is_pass else (239, 68, 68)
    decision_text = "FINAL RESULT: PASS" if is_pass else "FINAL RESULT: FAIL"

    pdf.set_line_width(0.3)
    pdf.rect(5, 5, 200, 287)
    
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(5, 5, 200, 45, 'F')
    
    try: pdf.image(LOGO_PATH, 10, 10, 35, 35)
    except: pass

    if photo_bytes:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(photo_bytes.getvalue())
            tmp_path = tmp.name
        try:
            pdf.image(tmp_path, 165, 10, 32, 32)
            os.unlink(tmp_path)
        except: pass

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

    return pdf.output(dest='S').encode('latin-1')

# --- Styling (Glassmorphism) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@400;700&display=swap');
    
    :root {
        --color-bg: #0f172a;
        --color-primary: #3b82f6;
        --color-secondary: #64748b;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }

    /* Secondary/Default buttons */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #fff !important;
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        filter: brightness(1.1);
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        background: linear-gradient(to right, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(to right, #3b82f6, #10b981) !important;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .glass-card { padding: 1rem !important; }
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
    }

    /* Remove white borders/boxes from streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] { border: none !important; }
    
    /* Clean up the text area */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        color: white !important;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    </style>
""", unsafe_allow_html=True)

# --- AI & Parsing Helpers ---
def get_api_key(): return os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")

def call_ai(messages, model=DEFAULT_MODEL):
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key: headers["Authorization"] = f"Bearer {api_key}"
    try:
        res = requests.post(KILO_API_URL, headers=headers, json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 1200}, timeout=45)
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {res.status_code} - See details in console")
            return None
    except Exception as e:
        st.error(f"Network Error: {str(e)}")
        return None

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages: text += page.extract_text()
    return text

# --- State ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
# Ensure user_info exists and has all required keys (fixing potential old session issues)
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}
else:
    for key in ["name", "email", "phone", "id"]:
        if key not in st.session_state.user_info:
            st.session_state.user_info[key] = ""

if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'questions' not in st.session_state: st.session_state.questions = []
if 'answers' not in st.session_state: st.session_state.answers = []
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'persistent_photo' not in st.session_state: st.session_state.persistent_photo = None
if 'interview_time' not in st.session_state: st.session_state.interview_time = None

# --- Pages ---
@st.dialog("Submit Interview?")
def confirm_submission():
    st.write("Are you sure you want to complete the interview? You won't be able to change your answers after this.")
    c1, c2 = st.columns(2)
    if c1.button("✅ Yes, Submit", use_container_width=True, type="primary"):
        with st.status("🚀 Processing submission...", expanded=True) as s:
            st.write("Gathering responses...")
            time.sleep(0.5)
            st.write("Finalizing session...")
            st.session_state.step = 'report'
        st.rerun()
    if c2.button("❌ No, Go Back", use_container_width=True):
        st.rerun()

def show_setup():
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; margin-top: -1.5rem; padding-bottom: 2rem; flex-wrap: wrap;">
            <img src="data:image/png;base64,{LOGO_BASE64}" width="100" style="filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.4));">
            <div style="text-align: left;">
                <h1 style="margin: 0; padding: 0; letter-spacing: 2px; font-weight: 800; color: #ffffff; line-height: 1.1; font-size: 2.2rem;">MANVER <span style="color: #60a5fa;">AI INTERVIEWER</span></h1>
                <p style="margin: 0.2rem 0 0 0; color: #60a5fa; font-size: 0.9rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">ADVANCED AI INTERVIEW PLATFORM</p>
            </div>
        </div>
        <div style="width: 100%; max-width: 600px; height: 2px; background: linear-gradient(90deg, transparent, #3b82f6, transparent); margin: 0 auto 1.5rem; border-radius: 10px;"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <script>
        // 1. Enter Navigation
        function setupEnterNavigation() {
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            inputs.forEach((input, index) => {
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const next = inputs[index + 1];
                        if (next) { next.focus(); } else {
                            input.blur();
                            setTimeout(() => {
                                const btn = window.parent.document.querySelector('button[kind="primary"]');
                                if (btn) btn.click();
                            }, 100);
                        }
                    }
                });
            });
        }

        function initListeners() {
            const speakBtn = window.parent.document.getElementById('speak-btn');
            if (speakBtn) {
                speakBtn.onclick = null;
                speakBtn.addEventListener('click', startSpeech);
            }
        }

        if (!window.enterNavSetup) { 
            setTimeout(setupEnterNavigation, 1000); 
            setInterval(initListeners, 2000);
            window.enterNavSetup = true; 
        }
        </script>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 🔑 Candidate Details")
        st.text_input("Full Name *", key="reg_name", placeholder="John Doe")
        st.text_input("Email ID *", key="reg_email", placeholder="john@example.com")
        st.text_input("Candidate ID *", key="reg_id", placeholder="CAND-001")
        st.text_input("Phone Number *", key="reg_phone", placeholder="+91 XXXX XXXX")
        
        st.write("### 📄 Assessment Basis")
        input_type = st.radio("Choose Input Type:", ["Upload Resume (PDF)", "Paste Job Description (JD)"], horizontal=True, label_visibility="collapsed")
        
        uploaded_file = None
        jd_text = ""
        
        if input_type == "Upload Resume (PDF)":
            uploaded_file = st.file_uploader("Upload PDF *", type=['pdf'], label_visibility="collapsed")
        else:
            jd_text = st.text_area("Paste Job Description (JD) *", height=150, placeholder="Example: Senior Software Engineer with 5+ years experience in Python...", label_visibility="collapsed")
        
        st.write("### 🧠 Intelligence Model")
        model = st.selectbox("Intelligence Model", ["kilo-auto/free", "minimax/minimax-m2.5:free"], label_visibility="collapsed")
        
        if st.button("🚀 Start Interview Session", type="primary", use_container_width=True):
            v_name = st.session_state.get("reg_name", "").strip()
            v_id = st.session_state.get("reg_id", "").strip()
            
            if not v_name or not v_id:
                st.error("⚠️ All detail fields are mandatory.")
            elif input_type == "Upload Resume (PDF)" and not uploaded_file:
                st.error("📄 Please upload your resume PDF.")
            elif input_type == "Paste Job Description (JD)" and not jd_text.strip():
                st.error("📝 Please paste the Job Description.")
            elif not st.session_state.persistent_photo:
                st.error("📸 Identity verification required. Capture your photo on the right.")
            elif 'mic_test_recording' not in st.session_state or st.session_state.mic_test_recording is None:
                st.error("🎤 Hardware Error: You must record a short test audio block to verify your microphone.")
            else:
                st.session_state.user_info = {"name": v_name, "id": v_id, "email": st.session_state.reg_email, "phone": st.session_state.reg_phone}
                from datetime import datetime
                st.session_state.interview_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with st.spinner("✨ Analyzing input and building path..."):
                    if input_type == "Upload Resume (PDF)":
                        input_content = extract_text_from_pdf(uploaded_file)
                        prompt_msg = "Analyze resume."
                    else:
                        input_content = jd_text
                        prompt_msg = "Analyze job description and identify key skills."
                    
                    res = call_ai([{"role": "system", "content": prompt_msg}, {"role": "user", "content": input_content}], model=model)
                    if res:
                        st.session_state.analysis = res
                        st.session_state.step = 'analysis'
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.write("### 🎙️ Hardware & Identity Check")
        
        # 🎤 Native Microphone Check (100% Reliability for permissions)
        st.info("🎤 **Step 1: Verify Microphone**")
        st.write("Record a quick 1-second audio clip to unlock the session.")
        mic_test = st.audio_input("Test Recording", key="mic_test_recording", label_visibility="collapsed")
        if mic_test:
            st.success("✅ Microphone Verified Successfully!")
        
        st.divider()
        
        st.info("👤 **Step 2: Capture Identity**")
        st.write("Click the camera icon below to manually capture your photo.")
        
        def sync_photo():
            if st.session_state.setup_cam is None: st.session_state.persistent_photo = None
            else: st.session_state.persistent_photo = st.session_state.setup_cam
            
        st.camera_input("Verify Photo", key="setup_cam", label_visibility="collapsed", on_change=sync_photo)
        
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, width=150)
            st.success("✅ Photo Verified")
        st.markdown('</div>', unsafe_allow_html=True)

def show_analysis():
    render_header()
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">'
                '<h1>🔍 CANDIDATE INSIGHTS</h1>'
                '</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="glass-card"><div style="color: #cbd5e1; line-height: 1.6;">{st.session_state.analysis}</div></div>', unsafe_allow_html=True)
    
    col_l, col_r, col_c = st.columns([1, 1, 1])
    with col_r:
        if st.button("✅ Confirm & Proceed", type="primary", use_container_width=True):
            with st.spinner("🚀 Generating technical questionnaire..."):
                prompt = "Generate 8 technical questions based on the candidate. One per line. No numbers."
                text = call_ai([{"role": "system", "content": prompt}, {"role": "user", "content": st.session_state.analysis}])
                if text:
                    st.session_state.questions = [q.strip() for q in text.split('\n') if len(q.strip()) > 10][:8]
                    st.session_state.answers = [""] * len(st.session_state.questions)
                    st.session_state.current_q = 0
                    st.session_state.step = 'interview'
                    st.rerun()

@st.fragment
def interview_content():
    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    st.progress((q_idx + 1) / total)
    
    # 📹 Q&A Left, Proctoring Right [3, 0.1, 0.7] - Optimized for smaller video
    c_qa, spacer, c_proc = st.columns([3, 0.1, 0.7], gap="small", vertical_alignment="top")
    
    with c_qa:
        st.markdown('<div class="glass-card" style="min-height: 520px; display: flex; flex-direction: column; justify-content: space-between;">', unsafe_allow_html=True)
        question = st.session_state.questions[q_idx]
        st.markdown(f'<div style="font-size: 1.6rem; font-weight: 800; color: #60a5fa; margin-bottom: 2rem;">{question}</div>', unsafe_allow_html=True)
        
        ans = st.text_area("ans_box", value=st.session_state.answers[q_idx], height=260, key=f"ans_ta_{q_idx}", placeholder="Explain your approach here...", label_visibility="collapsed")
        st.session_state.answers[q_idx] = ans
        
        st.write("") # Spacer
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1.2, 1.2])
        with col_nav1:
            if st.button("⬅️ Back", disabled=(q_idx == 0), use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()
        with col_nav2:
            st.markdown(f"""
                <button id="speak-btn" style="background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 0.75rem; border-radius: 12px; width: 100%; cursor: pointer; font-weight: 700; transition: all 0.2s; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">🎤 Voice Answer</button>
                <script>
                    function startSpeech() {{
                        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        const rec = new Recognition();
                        const btn = document.getElementById('speak-btn');
                        if (btn) {{ btn.style.background = '#ef4444'; btn.innerText = 'Listening...'; }}
                        rec.onresult = (e) => {{
                            const transcript = e.results[0][0].transcript;
                            const findAndFill = (root) => {{
                                if (!root) return false;
                                const textareas = root.querySelectorAll('textarea');
                                for (let t of textareas) {{
                                    if (t.id && t.id.includes('ans_ta_')) {{
                                        t.value += (t.value ? ' ' : '') + transcript;
                                        t.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                        return true;
                                    }}
                                }}
                                const iframes = root.querySelectorAll('iframe');
                                for (let f of iframes) {{ try {{ if (findAndFill(f.contentDocument)) return true; }} catch(e) {{}} }}
                                return false;
                            }};
                            findAndFill(document); findAndFill(window.parent.document);
                            if (btn) {{ btn.style.background = 'linear-gradient(135deg, #10b981, #059669)'; btn.innerText = '🎤 Voice Answer'; }}
                        }};
                        rec.onerror = () => {{ if (btn) {{ btn.style.background = 'linear-gradient(135deg, #10b981, #059669)'; btn.innerText = '🎤 Voice Answer'; }} }};
                        rec.start();
                    }}
                </script>
                <style>
                #MainMenu {{visibility: hidden;}}
                footer {{visibility: hidden;}}
                header {{visibility: hidden;}}
                button[title="View source"] {{display: none;}}
                .custom-footer {{
                    position: fixed; left: 0; bottom: 0; width: 100%;
                    background: rgba(15, 23, 42, 0.95); color: #64748b;
                    text-align: center; padding: 10px; font-size: 0.8rem;
                    z-index: 9999; border-top: 1px solid rgba(255,255,255,0.05);
                }}
                </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="custom-footer">© 2026 MANVER AI INTERVIEWER. ALL RIGHTS RESERVED.</div>', unsafe_allow_html=True)
        with col_nav3:
            label = "Finish & Submit ✨" if q_idx + 1 == total else "Next Item ➡️"
            if st.button(label, use_container_width=True, type="primary"):
                if q_idx + 1 < total:
                    st.session_state.current_q += 1
                    st.rerun()
                else: confirm_submission()
        st.markdown('</div>', unsafe_allow_html=True)

    with c_proc:
        st.markdown('<div class="glass-card" style="padding: 0.8rem; text-align: center; border-right: 4px solid #3b82f6;">', unsafe_allow_html=True)
        st.markdown('<div style="color: #60a5fa; font-weight: 700; margin-bottom: 0.5rem; font-size: 0.8rem;">📹 PROCTORING</div>', unsafe_allow_html=True)
        # Use a smaller camera input if possible via standard Streamlit (just smaller column)
        st.camera_input("Monitoring", key=f"proctor_session_9_{q_idx}", label_visibility="collapsed")
        st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 6px; border-radius: 8px; margin-top: 0.5rem; font-size: 0.7rem; font-weight: 600;">
                🛡️ LIVE MONITORING
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_interview():
    render_header()
    interview_content()

def show_report():
    info = st.session_state.user_info
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">'
                '<h1>📊 FINAL EVALUATION</h1>'
                '</div>', unsafe_allow_html=True)
    
    with st.spinner("🤖 AI is analyzing your performance..."):
        transcript = ""
        for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
            transcript += f"Q{i+1}: {q}\nA: {a}\n\n"
            
        res = call_ai([
            {"role": "system", "content": "Create report for Interview. YOU MUST START THE REPORT WITH 'RESULT: PASS' or 'RESULT: FAIL' based on performance, then provide details."},
            {"role": "user", "content": f"Candidate: {info.get('name', 'N/A')}\nID: {info.get('id', 'N/A')}\nEmail: {info.get('email', 'N/A')}\nDate: {st.session_state.interview_time}\n\nTranscript:\n{transcript}"}
        ])
    
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        # Decision Badge
        is_pass = "PASS" in str(res).upper()
        badge_bg = "rgba(16, 185, 129, 0.2)" if is_pass else "rgba(239, 68, 68, 0.2)"
        badge_border = "#10b981" if is_pass else "#ef4444"
        badge_text = "🟢 RESULT: PASS" if is_pass else "🔴 RESULT: FAIL"
        
        st.markdown(f'<div style="background: {badge_bg}; border: 1px solid {badge_border}; color: white; padding: 1.2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem; font-weight: 800; font-size: 1.5rem; letter-spacing: 2px;">{badge_text}</div>', unsafe_allow_html=True)
        
        st.write(f"### 📋 Detailed Analysis")
        st.markdown(f'<div style="color: #cbd5e1; line-height: 1.7; font-size: 1.05rem;">{res}</div>', unsafe_allow_html=True)
        st.divider()
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Start New"): st.session_state.clear(); st.rerun()

if st.session_state.step == 'setup': show_setup()
elif st.session_state.step == 'analysis': show_analysis()
elif st.session_state.step == 'interview': show_interview()
elif st.session_state.step == 'report': show_report()





