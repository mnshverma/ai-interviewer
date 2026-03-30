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
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'questions' not in st.session_state: st.session_state.questions = []
if 'answers' not in st.session_state: st.session_state.answers = []
if 'current_q' not in st.session_state: st.session_state.current_q = 0
if 'transcript' not in st.session_state: st.session_state.transcript = []
if 'speech_text' not in st.session_state: st.session_state.speech_text = ""

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
                import re
                # Improved regex to catch various list patterns: 1. , 1) , - , * , Q1: etc.
                questions = []
                for line in text.split('\n'):
                    line = line.strip()
                    if not line: continue
                    # Match patterns like "1. ", "1) ", "Q1: ", "- ", "* "
                    match = re.match(r'^(?:\d+[\.\)]|Q\d+:|[\-\*])\s*(.*)', line)
                    if match:
                        q_text = match.group(1).strip()
                        if q_text: questions.append(q_text)
                    elif len(line) > 10 and line[0].isdigit(): # Simple fallback for "1 Question"
                        questions.append(line)
                
                if not questions: 
                    # If still no questions, split by lines and take long enough ones
                    questions = [q.strip() for q in text.split('\n') if len(q.strip()) > 10][:8]
                
                if not questions: questions = [text] 
                st.session_state.questions = questions[:8]
                st.session_state.answers = [""] * len(st.session_state.questions)
                st.session_state.step = 'interview'
                st.rerun()

def show_interview():
    st.title("🎙️ Live Interview Session")
    q_idx = st.session_state.current_q
    total = len(st.session_state.questions)
    
    if total == 0:
        st.error("No questions found! Restart the interview.")
        if st.button("🔄 Restart"): st.session_state.clear(); st.rerun()
        return

    # Progress bar with nice visual
    progress = (q_idx + 1) / total
    st.progress(progress)
    st.subheader(f"Question {q_idx + 1} of {total}")

    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown('<div class="glass-card" style="min-height: 400px; display: flex; flex-direction: column; justify-content: space-between;">', unsafe_allow_html=True)
        
        # Display current question
        question = st.session_state.questions[q_idx]
        st.markdown(f'<div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 2rem; color: #60a5fa;">{question}</div>', unsafe_allow_html=True)
        
        # Answer textarea - using key to persist between navigation
        ans = st.text_area("Your Answer", value=st.session_state.answers[q_idx], height=200, key=f"ans_{q_idx}", placeholder="Type your answer or use the 'Speak' button...", label_visibility="collapsed")
        st.session_state.answers[q_idx] = ans # Sync back to state
        
        # Controls
        b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
        
        # Previous Button
        if b1.button("⬅️ Previous", disabled=(q_idx == 0)):
            st.session_state.current_q -= 1
            st.rerun()
            
        # Speak Button (HTML/JS)
        with b2:
            st.markdown(f"""
                <button onclick="startSpeech()" style="background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; color: #60a5fa; padding: 0.8rem; border-radius: 12px; width: 100%; cursor: pointer; transition: 0.3s; height: 100%;">🎙️ Speak</button>
                <script>
                    function startSpeech() {{
                        const recog = window.SpeechRecognition || window.webkitSpeechRecognition;
                        if (!recog) {{ alert('Speech not supported'); return; }}
                        const r = new recog();
                        r.onresult = (e) => {{
                            const text = e.results[0][0].transcript;
                            const t = window.parent.document.querySelector('textarea[aria-label="Your Answer"]');
                            if (t) {{
                                t.value += (t.value ? ' ' : '') + text;
                                t.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            }}
                        }};
                        r.start();
                    }}
                </script>
            """, unsafe_allow_html=True)

        # Skip Button
        if b3.button("⏩ Skip"):
            if not st.session_state.answers[q_idx]:
                st.session_state.answers[q_idx] = "Skipped"
            if q_idx + 1 < total:
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.session_state.step = 'report'
                st.rerun()

        # Next/Finish Button
        action = "Finish ✨" if q_idx + 1 == total else "Next ➡️"
        if b4.button(action):
            if q_idx + 1 < total:
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.session_state.step = 'report'
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 📹 Video Feed & AI")
        st.camera_input("Proctoring", label_visibility="collapsed")
        st.info("Tip: Looking directly at the camera improves your confidence score.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_report():
    st.title("📊 Final Evaluation Report")
    with st.spinner("Calculating Score..."):
        # Compile transcript from questions and answers
        transcript_lines = []
        for q, a in zip(st.session_state.questions, st.session_state.answers):
            transcript_lines.append(f"Q: {q}\nA: {a}")
        transcript = "\n\n".join(transcript_lines)
        
        res = call_ai([
            {"role": "system", "content": "Analyze the interview transcript. Provide: 1. OVERALL SCORE [0-100] 2. STATUS [PASS/FAIL] 3. Detailed Feedback for each question."}, 
            {"role": "user", "content": f"Interview Data:\n{transcript}"}
        ])
        
        if res:
            if "PASS" in res.upper(): st.success("🎉 CONGRATULATIONS: YOU PASSED!")
            else: st.error("📉 EVALUATION: FAIL")
            st.markdown(f'<div class="glass-card">{res}</div>', unsafe_allow_html=True)
        else:
            st.error("Could not generate report. Please try again.")

    if st.button("🔄 Restart Interview"): st.session_state.clear(); st.rerun()

if st.session_state.step == 'setup': show_setup()
elif st.session_state.step == 'analysis': show_analysis()
elif st.session_state.step == 'interview': show_interview()
elif st.session_state.step == 'report': show_report()
