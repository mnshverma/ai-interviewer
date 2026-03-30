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
        --color-secondary: #475569;
        --color-accent: #60a5fa;
        --color-glass: rgba(15, 23, 42, 0.6);
        --color-border: rgba(59, 130, 246, 0.2);
    }
    
    .stApp {
        background: radial-gradient(circle at 0% 0%, #1e293b, #0f172a);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }
    
    .glass-card {
        background: var(--color-glass);
        backdrop-filter: blur(20px);
        border: 1px solid var(--color-border);
        border-radius: 1.5rem;
        padding: 2.5rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 8px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa, #3b82f6);
        transform: translateY(-2px);
    }
    
    /* Dedicated class for Skip/Secondary buttons */
    div[data-testid="stButton"] button:has(div:contains("Skip")) { 
        background: linear-gradient(135deg, #475569, #1e293b) !important; 
        box-shadow: none !important; 
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        background: linear-gradient(to right, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(to right, #3b82f6, #60a5fa) !important;
    }
    
    /* Clean up phantom boxes */
    div[data-testid="stVerticalBlockBorderWrapper"] { border: none !important; background: transparent !important; box-shadow: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- AI & Parsing Helpers ---
def get_api_key(): return os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")

def call_ai(messages, model=DEFAULT_MODEL):
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key: headers["Authorization"] = f"Bearer {api_key}"
    try:
        res = requests.post(KILO_API_URL, headers=headers, json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 1200}, timeout=35)
        return res.json()["choices"][0]["message"]["content"] if res.status_code == 200 else None
    except: return None

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages: text += page.extract_text()
    return text

# --- State ---
for key in ['step', 'analysis', 'questions', 'current_q', 'transcript', 'speech_text']:
    if key not in st.session_state: st.session_state[key] = 'setup' if key == 'step' else 0 if key == 'current_q' else [] if key in ['questions', 'transcript'] else ""

# --- Pages ---
def show_setup():
    st.title("🤖 Manver AI Interviewer")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 📄 Resume Analysis")
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], label_visibility="collapsed")
        model = st.selectbox("Model", ["kilo-auto/free", "minimax/minimax-m2.5:free"], label_visibility="collapsed")
        if uploaded_file and st.button("🚀 Start Interview"):
            with st.spinner("Analyzing..."):
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
        st.camera_input("Camera", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

def show_analysis():
    st.title("🔍 Candidate Insights")
    st.markdown(f'<div class="glass-card">{st.session_state.analysis}</div>', unsafe_allow_html=True)
    if st.button("✅ Confirm & Proceed"):
        with st.spinner("Preparing Questions..."):
            text = call_ai([{"role": "system", "content": "Generate 8 tech questions."}, {"role": "user", "content": st.session_state.analysis}])
            if text:
                questions = [q.split('.',1)[1].strip() if '.' in q else q for q in text.split('\n') if q.strip() and (q[0].isdigit() or (len(q) > 1 and q[1].isdigit()))]
                if not questions: questions = [text] # Fallback to using the whole text as one question if parsing fails
                st.session_state.questions = questions[:8]
                st.session_state.step = 'interview'
                st.rerun()

def show_interview():
    st.title("🎙️ Live Interview Session")
    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    st.progress(q_idx / total if total > 0 else 0)
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write(f"### Question {q_idx + 1} of {total}")
        st.markdown(f"**{st.session_state.questions[q_idx]}**")
        ans = st.text_area("Ans", value=st.session_state.speech_text, height=180, label_visibility="collapsed", placeholder="Type or speak...")
        b1, b2, b3 = st.columns([1,1,1])
        if b1.button("➡️ Next"):
            if ans.strip():
                st.session_state.transcript.append({"q": st.session_state.questions[q_idx], "a": ans})
                st.session_state.speech_text = ""
                if q_idx + 1 < total: st.session_state.current_q += 1
                else: st.session_state.step = 'report'
                st.rerun()
        if b2.button("⏩ Skip"):
            st.session_state.transcript.append({"q": st.session_state.questions[q_idx], "a": "Skipped"})
            st.session_state.speech_text = ""
            if q_idx + 1 < total: st.session_state.current_q += 1
            else: st.session_state.step = 'report'
            st.rerun()
        with b3:
            st.markdown("""<button id="m" onclick="s()" style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.4);color:#60a5fa;padding:10px;border-radius:10px;cursor:pointer;width:100%;">🎙️ Speak</button>
            <script>function s(){if(!window.webkitSpeechRecognition)return;const r=new webkitSpeechRecognition();r.onresult=(e)=>{const t=e.results[0][0].transcript;const a=window.parent.document.querySelector('textarea');a.value+=(a.value?' ':'')+t;a.dispatchEvent(new Event('input',{bubbles:true}));};r.start();}</script>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 🔴 PROCTORING")
        st.camera_input("Feed", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

def show_report():
    st.title("📊 Final Evaluation Report")
    with st.spinner("Calculating Score..."):
        transcript = "\n".join([f"Q: {i['q']}\nA: {i['a']}" for i in st.session_state.transcript])
        res = call_ai([{"role": "system", "content": "Provide structured report: SCORE [0-100], RESULT [PASS/FAIL], FEEDBACK."}, {"role": "user", "content": transcript}])
        if res:
            if "PASS" in res.upper(): st.success("🎉 CONGRATULATIONS: YOU PASSED!")
            else: st.error("📉 EVALUATION: FAIL")
            st.markdown(f'<div class="glass-card">{res}</div>', unsafe_allow_html=True)
    if st.button("🔄 Restart"): st.session_state.clear(); st.rerun()

if st.session_state.step == 'setup': show_setup()
elif st.session_state.step == 'analysis': show_analysis()
elif st.session_state.step == 'interview': show_interview()
elif st.session_state.step == 'report': show_report()
