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
st.set_page_config(page_title="Manver AI Interviewer", page_icon="🤖", layout="wide")

# --- Configuration ---
KILO_API_URL = "https://api.kilo.ai/api/gateway/chat/completions"
DEFAULT_MODEL = "kilo-auto/free"

# --- Global Header ---
def render_header():
    if 'user_info' not in st.session_state or not st.session_state.user_info.get("name"): return
    
    st.markdown('<div class="glass-card" style="margin-bottom: 2rem; padding: 1rem;">', unsafe_allow_html=True)
    h_c1, h_c2, h_c3 = st.columns([1, 4, 2])
    
    with h_c1:
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, width=100)
            
    with h_c2:
        info = st.session_state.user_info
        st.markdown(f"""
            <div style="padding-top: 10px;">
                <h2 style="margin:0; color:#3b82f6; text-transform: uppercase;">{info['name']}</h2>
                <p style="margin:0; color:#94a3b8; font-family:monospace; font-size: 1.1rem;">CANDIDATE ID: {info['id']}</p>
                <div style="margin-top:5px; font-size:0.85rem; color:#64748b;">🛡️ IDENTITY VERIFIED | 🎤 AUDIO CHECK: OK</div>
            </div>
        """, unsafe_allow_html=True)
        
    with h_c3:
        st.markdown(f"""
            <div style="text-align: right; padding-top: 5px;">
                <div style="color: #60a5fa; font-weight: 700; font-size: 1.2rem;">📅 {st.session_state.interview_time.split(' ')[0]}</div>
                <div style="color: #94a3b8; font-weight: 600; font-size: 1.1rem;">⏱️ {st.session_state.interview_time.split(' ')[1]}</div>
                <div style="margin-top: 10px; font-size: 0.75rem; background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 4px 8px; border-radius: 6px; display: inline-block;">LIVE SESSION ACTIVE</div>
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

    # 🖼️ Page Border
    pdf.set_line_width(0.5)
    pdf.rect(5, 5, 200, 287)
    
    # Header Background
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(5, 5, 200, 45, 'F')
    
    # Photo Border & Image
    if photo_bytes:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(photo_bytes.getvalue())
            tmp_path = tmp.name
        try:
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(10, 10, 32, 32, 'F')
            pdf.image(tmp_path, 11, 11, 30, 30)
            os.unlink(tmp_path)
        except: pass

    # Title & Info in Header
    pdf.set_xy(48, 12)
    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, info.get('name', 'N/A').upper(), 0, 1)
    
    pdf.set_xy(48, 22)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(100, 6, f"ID: {info.get('id', 'N/A')} | EMAIL: {info.get('email', 'N/A')}", 0, 1)
    
    pdf.set_xy(48, 28)
    pdf.cell(100, 6, f"TIME: {st.session_state.interview_time}", 0, 1)

    # Status Badge below header
    pdf.set_fill_color(*decision_color)
    pdf.rect(5, 50, 200, 15, 'F')
    pdf.set_xy(5, 50)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(200, 15, decision_text, 0, 1, 'C')

    # Main Content
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
st.set_page_config(page_title="Manver AI Interviewer", page_icon="🤖", layout="wide")

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
    
    /* Remove white borders/boxes from streamlit */
    div[data-testid="stVerticalBlockBorderWrapper"] { border: none !important; }
    
    /* Clean up the text area */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        color: white !important;
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
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">'
                '<h1>🤖 MANVER AI INTERVIEW</h1>'
                '<p style="color: #94a3b8; font-size: 1.1rem;">Professional Automated Screening System</p>'
                '</div>', unsafe_allow_html=True)
    
    # 🎤 Microphone Verification Logic (JS-to-Python Bridge)
    # We use a hidden input and a button to confirm the mic works
    mic_ready = st.checkbox("mic_verified", key="mic_verified", label_visibility="collapsed")
    
    st.markdown(f"""
        <script>
        // 1. Enter Navigation
        function setupEnterNavigation() {{
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            inputs.forEach((input, index) => {{
                input.addEventListener('keydown', (e) => {{
                    if (e.key === 'Enter') {{
                        e.preventDefault();
                        const next = inputs[index + 1];
                        if (next) {{ next.focus(); }} else {{
                            input.blur();
                            setTimeout(() => {{
                                const btn = window.parent.document.querySelector('button[kind="primary"]');
                                if (btn) btn.click();
                            }}, 100);
                        }}
                    }}
                }});
            }});
        }}

        // 2. Hardware Permission Check (Manual Trigger)
        async function runManualMicCheck() {{
            const statusEl = window.parent.document.getElementById('mic-status-text');
            const checkBtn = window.parent.document.getElementById('mic-check-btn');
            statusEl.innerHTML = '🕒 Requesting Access...';
            statusEl.style.color = '#facc15';
            
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                stream.getTracks().forEach(track => track.stop());
                
                statusEl.innerHTML = '✅ MICROPHONE READY';
                statusEl.style.color = '#10b981';
                checkBtn.style.display = 'none';
                
                // Signal back to Streamlit (Hidden checkbox click simulation)
                const cb = window.parent.document.querySelector('input[aria-label="mic_verified"]');
                if (cb) {{ cb.click(); }}
            }} catch (err) {{
                statusEl.innerHTML = '❌ MICROPHONE BLOCKED | ' + err.message;
                statusEl.style.color = '#ef4444';
                alert('Microphone permission denied. Please enable it in your browser settings to proceed.');
            }}
        }}

        if (!window.enterNavSetup) {{ 
            setTimeout(setupEnterNavigation, 1000); 
            window.enterNavSetup = true; 
        }}
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
        
        st.write("### 📄 Resume Analysis")
        uploaded_file = st.file_uploader("Upload PDF *", type=['pdf'], label_visibility="collapsed")
        model = st.selectbox("Intelligence Model", ["kilo-auto/free", "minimax/minimax-m2.5:free"], label_visibility="collapsed")
        
        if st.button("🚀 Start Interview Session", type="primary", use_container_width=True):
            v_name = st.session_state.get("reg_name", "").strip()
            v_id = st.session_state.get("reg_id", "").strip()
            
            if not v_name or not v_id:
                st.error("⚠️ All detail fields are mandatory.")
            elif not uploaded_file:
                st.error("📄 Please upload your resume.")
            elif not st.session_state.persistent_photo:
                st.error("📸 Identity verification required. Use the capture tool on the right.")
            elif not st.session_state.mic_verified:
                st.error("🎤 Hardware Error: You must verify your microphone before proceeding.")
            else:
                st.session_state.user_info = {"name": v_name, "id": v_id, "email": st.session_state.reg_email, "phone": st.session_state.reg_phone}
                from datetime import datetime
                st.session_state.interview_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with st.spinner("✨ Analyzing profile and building path..."):
                    text = extract_text_from_pdf(uploaded_file)
                    res = call_ai([{"role": "system", "content": "Analyze resume."}, {"role": "user", "content": text}], model=model)
                    if res:
                        st.session_state.analysis = res
                        st.session_state.step = 'analysis'
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card" style="text-align: center;">', unsafe_allow_html=True)
        st.write("### 📸 Identity & Hardware Check")
        
        # 🎤 Microphone Interface
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.4); border-radius: 12px; padding: 1.2rem; margin-bottom: 2rem; border: 1px solid rgba(255,255,255,0.05); text-align: left;">
                <div id="mic-status-text" style="font-weight: 700; color: #facc15; margin-bottom: 0.8rem;">🎧 MICROPHONE VERIFICATION</div>
                <button id="mic-check-btn" onclick="runManualMicCheck()" style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 600;">Run Audio Test</button>
            </div>
        """, unsafe_allow_html=True)
        
        st.warning("👤 **IDENTITY CAPTURE REQUIRED**")
        st.write("Click the camera icon below to manually capture your photo.")
        
        # Camera Check (Native)
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
    
    # 📹 Proctoring Camera & Q&A Layout
    c1, spacer, c2 = st.columns([1, 0.1, 2], gap="small")
    
    with c1:
        st.markdown('<div class="glass-card" style="padding: 1rem; text-align: center;">', unsafe_allow_html=True)
        st.write("🎙️ **LIVE PROCTORING**")
        st.camera_input("Monitoring", key=f"proctor_v3_{q_idx}", label_visibility="collapsed")
        st.warning("⚠️ Identity verified. Monitoring active.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card" style="min-height: 480px; display: flex; flex-direction: column; justify-content: space-between;">', unsafe_allow_html=True)
        question = st.session_state.questions[q_idx]
        st.markdown(f'<div style="font-size: 1.5rem; font-weight: 700; color: #60a5fa; margin-bottom: 2rem;">{question}</div>', unsafe_allow_html=True)
        
        ans = st.text_area("ans_box", value=st.session_state.answers[q_idx], height=220, key=f"ans_ta_{q_idx}", placeholder="Express your answer here...", label_visibility="collapsed")
        st.session_state.answers[q_idx] = ans
        
        st.write("") # Spacer
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
        with col_nav1:
            if st.button("⬅️ Previous", disabled=(q_idx == 0), use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()
        with col_nav2:
            st.markdown(f"""
                <button id="speak-btn" onclick="startSpeech()" style="background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 0.75rem; border-radius: 12px; width: 100%; cursor: pointer; font-weight: 700; transition: all 0.2s; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">🎤 Voice Answer</button>
                <script>
                    function startSpeech() {{
                        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        if (!Recognition) {{ alert('Speech Recognition not supported in this browser.'); return; }}
                        const rec = new Recognition();
                        const btn = document.getElementById('speak-btn');
                        btn.style.background = '#ef4444'; btn.innerText = 'Listening...';
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
                            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)'; btn.innerText = '🎤 Voice Answer';
                        }};
                        rec.onerror = () => {{ btn.style.background = 'linear-gradient(135deg, #10b981, #059669)'; btn.innerText = '🎤 Voice Answer'; }};
                        rec.start();
                    }}
                </script>
                <style>
                #MainMenu, footer, header {visibility: hidden;}
                button[title="View source"] {display: none;}
                .custom-footer {
                    position: fixed; left: 0; bottom: 0; width: 100%;
                    background: rgba(15, 23, 42, 0.95); color: #64748b;
                    text-align: center; padding: 8px; font-size: 0.75rem;
                    z-index: 9999; border-top: 1px solid rgba(255,255,255,0.05);
                }
                </style>
            """, unsafe_allow_html=True)
            st.markdown('<div class="custom-footer">© 2026 MANVER AI INTERVIEWER. ALL RIGHTS RESERVED.</div>', unsafe_allow_html=True)
        with col_nav3:
            label = "Submit Interview ✨" if q_idx + 1 == total else "Next Question ➡️"
            if st.button(label, use_container_width=True, type="primary"):
                if q_idx + 1 < total:
                    st.session_state.current_q += 1
                    st.rerun()
                else: confirm_submission()
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





