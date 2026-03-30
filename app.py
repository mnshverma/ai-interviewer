import streamlit as st
import os
import requests
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import time

# --- Setup ---
load_dotenv()

# Configuration
KILO_API_URL = "https://api.kilo.ai/api/gateway/chat/completions"
DEFAULT_MODEL = "kilo-auto/free"

# --- Styling (Glassmorphism) ---
st.set_page_config(page_title="Manver AI Interviewer", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Outfit:wght@400;700&display=swap');
    
    :root {
        --color-bg: #0f172a;
        --color-primary: #3b82f6;
        --color-secondary: #64748b;
        --color-accent: #10b981;
        --color-glass: rgba(30, 41, 59, 0.7);
        --color-border: rgba(255, 255, 255, 0.1);
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, #1e293b 0%, #0f172a 90%);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    .glass-card {
        background: var(--color-glass);
        backdrop-filter: blur(12px);
        border: 1px solid var(--color-border);
        border-radius: 1.25rem;
        padding: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 0.5rem 1rem !important;
    }

    /* Primary buttons */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
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
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'questions' not in st.session_state: st.session_state.questions = []
if 'answers' not in st.session_state: st.session_state.answers = []
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'persistent_photo' not in st.session_state: st.session_state.persistent_photo = None

# --- Pages ---
@st.dialog("Submit Interview?")
def confirm_submission():
    st.write("Are you sure you want to complete the interview? You won't be able to change your answers after this.")
    c1, c2 = st.columns(2)
    if c1.button("✅ Yes, Submit", use_container_width=True, type="primary"):
        st.session_state.step = 'report'
        st.rerun()
    if c2.button("❌ No, Go Back", use_container_width=True):
        st.rerun()

def show_setup():
    st.title("🤖 Manver AI Interviewer")
    
    c1, c2 = st.columns([1, 1], gap="medium")
    
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 👤 Candidate Details")
        
        name = st.text_input("Full Name *", key="reg_name", placeholder="John Doe")
        email = st.text_input("Email ID *", key="reg_email", placeholder="john@example.com")
        c_id = st.text_input("Candidate ID *", key="reg_id", placeholder="CAND-001")
        phone = st.text_input("Phone Number *", key="reg_phone", placeholder="+91 XXXX XXXX")
        
        st.write("### 📄 Resume Analysis")
        uploaded_file = st.file_uploader("Upload PDF *", type=['pdf'], label_visibility="collapsed")
        model = st.selectbox("Model", ["kilo-auto/free", "minimax/minimax-m2.5:free"], label_visibility="collapsed")
        
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            if not name.strip() or not email.strip() or not c_id.strip() or not phone.strip() or not uploaded_file:
                st.error("Please fill all fields and upload your resume.")
            elif not st.session_state.persistent_photo:
                st.error("Identity verification required! Please capture your photo on the right.")
            else:
                st.session_state.user_info = {"name": name, "email": email, "id": c_id, "phone": phone}
                with st.spinner("Analyzing profile..."):
                    text = extract_text_from_pdf(uploaded_file)
                    res = call_ai([{"role": "system", "content": "Analyze resume."}, {"role": "user", "content": text}], model=model)
                    if res:
                        st.session_state.analysis = res
                        st.session_state.step = 'analysis'
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 📹 System Check")
        st.info("Identity verification is mandatory.")
        
        # Using a separate key and saving it immediately to persistence
        cam_img = st.camera_input("Verify Identity", key="setup_camera")
        if cam_img:
            st.session_state.persistent_photo = cam_img
            st.success("✅ Identity Captured!")
        elif st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, caption="Verification Preview")
            
        st.markdown("""
            <div style="margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
                <strong>🎙️ Audio Check:</strong> Microphone and Camera permissions are required for the live session.
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_analysis():
    st.title("🔍 Candidate Insights")
    st.markdown(f'<div class="glass-card">{st.session_state.analysis}</div>', unsafe_allow_html=True)
    if st.button("✅ Confirm & Proceed", type="primary"):
        with st.spinner("Generating questions..."):
            prompt = "Generate 8 technical questions based on the candidate. One per line. No numbers."
            text = call_ai([{"role": "system", "content": prompt}, {"role": "user", "content": st.session_state.analysis}])
            if text:
                st.session_state.questions = [q.strip() for q in text.split('\n') if len(q.strip()) > 10][:8]
                st.session_state.answers = [""] * len(st.session_state.questions)
                st.session_state.current_q = 0
                st.session_state.step = 'interview'
                st.rerun()

def show_interview():
    st.title("🎙️ Live Session")
    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    if total == 0:
        st.warning("Repairing questions flow...")
        if st.button("🔄 Restart Setup"): st.session_state.step = 'setup'; st.rerun()
        return

    st.progress((q_idx + 1) / total)
    st.write(f"**Step {q_idx + 1} of {total}** | {st.session_state.user_info['name']}")

    c1, c2 = st.columns([3, 1], gap="small")
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        question = st.session_state.questions[q_idx]
        st.markdown(f'<div style="font-size: 1.4rem; font-weight: 700; color: #60a5fa; margin-bottom: 1rem;">{question}</div>', unsafe_allow_html=True)
        
        # Correctly keyed text area
        ans = st.text_area("ans_box", value=st.session_state.answers[q_idx], height=180, key=f"ans_ta_{q_idx}", placeholder="Your answer...", label_visibility="collapsed")
        st.session_state.answers[q_idx] = ans
        
        col_prev, col_speak, col_next = st.columns([1, 1, 1])
        with col_prev:
            if st.button("⬅️ Back", disabled=(q_idx == 0), use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()
        with col_speak:
            # More robust Speak button with broader JS search
            st.markdown(f"""
                <button id="speak-btn" onclick="startSpeech()" style="background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 0.7rem; border-radius: 12px; width: 100%; cursor: pointer; font-weight: 700;">🎤 Speak</button>
                <script>
                    function startSpeech() {{
                        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        if (!Recognition) {{ alert('Speech not supported in this browser.'); return; }}
                        const rec = new Recognition();
                        const btn = document.getElementById('speak-btn');
                        btn.style.background = '#ef4444';
                        btn.innerText = 'Listening...';
                        
                        rec.onresult = (e) => {{
                            const transcript = e.results[0][0].transcript;
                            // Search both current and parent documents to overcome iframe isolation
                            const docs = [document, window.parent.document];
                            let found = false;
                            for (let doc of docs) {{
                                try {{
                                    const textareas = doc.querySelectorAll('textarea');
                                    for (let t of textareas) {{
                                        if (t.id && t.id.includes('ans_ta_')) {{
                                            t.value += (t.value ? ' ' : '') + transcript;
                                            t.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                            found = true;
                                            break;
                                        }}
                                    }}
                                }} catch (e) {{ console.log('Iframe access restriction:', e); }}
                                if (found) break;
                            }}
                            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                            btn.innerText = '🎤 Speak';
                        }};
                        rec.onerror = () => {{
                            btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                            btn.innerText = '🎤 Speak';
                        }};
                        rec.start();
                    }}
                </script>
            """, unsafe_allow_html=True)
        with col_next:
            label = "Finish ✨" if q_idx + 1 == total else "Next ➡️"
            if st.button(label, use_container_width=True, type="primary"):
                if q_idx + 1 < total:
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    confirm_submission() # Trigger st.dialog
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card" style="padding: 1rem; text-align: center;">', unsafe_allow_html=True)
        st.write("📸 **Verified**")
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo, use_container_width=True)
        else:
            st.error("Photo Lost! Restart Setup.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_report():
    st.title("📊 Final Report")
    info = st.session_state.user_info
    
    with st.spinner("Generating summary..."):
        transcript = ""
        for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
            transcript += f"Q{i+1}: {q}\\nA: {a}\\n\\n"
            
        res = call_ai([
            {"role": "system", "content": "Create report for Interview."},
            {"role": "user", "content": f"Candidate: {info['name']}\\nID: {info['id']}\\nEmail: {info['email']}\\n\\nTranscript:\\n{transcript}"}
        ])
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write(f"### {info['name']} (ID: {info['id']})")
        st.write(f"📧 {info['email']} | 📞 {info['phone']}")
        st.divider()
        if res:
            st.write(res)
            report_text = f"Candidate: {info['name']}\\nID: {info['id']}\\nEvaluation:\\n{res}\\n\\nTranscript:\\n{transcript}"
            st.download_button("📥 Download PDF/TXT", report_text, file_name=f"Report_{info['id']}.txt", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### Identity")
        if st.session_state.persistent_photo:
            st.image(st.session_state.persistent_photo)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔄 Start New"): st.session_state.clear(); st.rerun()

if st.session_state.step == 'setup': show_setup()
elif st.session_state.step == 'analysis': show_analysis()
elif st.session_state.step == 'interview': show_interview()
elif st.session_state.step == 'report': show_report()



