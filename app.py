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
st.set_page_config(page_title="Manvar AI Interviewer", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    :root {
        --color-bg: #0f172a;
        --color-primary: #3b82f6;
        --color-glass: rgba(30, 41, 59, 0.7);
        --color-border: rgba(59, 130, 246, 0.2);
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f1f5f9;
    }
    
    .glass-card {
        background: var(--color-glass);
        backdrop-filter: blur(12px);
        border: 1px solid var(--color-border);
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.5);
    }
    
    h1, h2, h3 {
        background: linear-gradient(to right, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def get_api_key():
    return os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")

def call_ai(messages, model=DEFAULT_MODEL):
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = requests.post(
            KILO_API_URL,
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        if response.status_code != 200:
            st.error(f"AI Gateway Error: {response.status_code}")
            return None
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# --- State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 'setup'
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'transcript' not in st.session_state:
    st.session_state.transcript = []

# --- Pages ---
def show_setup():
    st.title("🤖 Manvar AI Interviewer")
    st.subheader("Your Intelligent Recruitment Partner (Python Version)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 📄 Step 1: Upload Resume")
        uploaded_file = st.file_uploader("Choose a PDF Resume", type=['pdf'])
        
        st.write("### ⚙️ Interview Settings")
        model = st.selectbox("AI Model (Free Tier)", [
            "kilo-auto/free",
            "minimax/minimax-m2.5:free",
            "z-ai/glm-5:free",
            "corethink:free"
        ])
        
        if uploaded_file and st.button("🚀 Start Analysis"):
            with st.spinner("Processing Resume..."):
                text = extract_text_from_pdf(uploaded_file)
                st.session_state.resume_text = text
                
                # Analysis Prompt
                analysis = call_ai([
                    {"role": "system", "content": "You are a senior recruiter analyzing resumes."},
                    {"role": "user", "content": f"Analyze this resume and extract key skills, experience level, and role alignment:\n\n{text}"}
                ], model=model)
                
                if analysis:
                    st.session_state.analysis = analysis
                    st.session_state.step = 'analysis'
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### 📹 Video & Audio Check")
        # In Streamlit, camera_input is a common way to show the feed
        st.camera_input("Check your webcam feed")
        st.info("Ensure your microphone is clear for the audio session.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_analysis():
    st.title("🔍 Candidate Profile Analysis")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.analysis)
    
    if st.button("✅ Confirm & Begin Interview"):
        with st.spinner("Generating Interview Questions..."):
            questions_text = call_ai([
                {"role": "system", "content": f"You are an interviewer. Based on this analysis, generate 8 technical questions: {st.session_state.analysis}"},
                {"role": "user", "content": "Generate 8 progressive interview questions formatted as a numbered list."}
            ])
            
            if questions_text:
                # Parse questions
                lines = [line.strip() for line in questions_text.split('\n') if line.strip()]
                st.session_state.questions = [q[3:] if q[0:2].isdigit() else q for q in lines if q[0].isdigit()]
                st.session_state.step = 'interview'
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_interview():
    st.title("🎙️ Live Interview Session")
    
    q_index = st.session_state.current_q
    total_q = len(st.session_state.questions)
    
    # Progress Bar
    st.progress(q_index / total_q)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="glass-card" style="height: 400px;">', unsafe_allow_html=True)
        st.write(f"### Question {q_index + 1} of {total_q}")
        st.markdown(f"**{st.session_state.questions[q_index]}**")
        
        answer = st.text_area("Your Response", height=150, placeholder="Type your answer here...")
        
        c1, c2 = st.columns(2)
        if c1.button("➡️ Next Question"):
            if answer.strip():
                st.session_state.transcript.append({
                    "q": st.session_state.questions[q_index],
                    "a": answer
                })
                if q_index + 1 < total_q:
                    st.session_state.current_q += 1
                else:
                    st.session_state.step = 'report'
                st.rerun()
            else:
                st.warning("Please provide an answer or skip.")
        
        if c2.button("⏩ Skip Question"):
            st.session_state.transcript.append({
                "q": st.session_state.questions[q_index],
                "a": "(Skipped)"
            })
            if q_index + 1 < total_q:
                st.session_state.current_q += 1
            else:
                st.session_state.step = 'report'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card" style="height: 400px; display: flex; align-items: center; justify-content: center;">', unsafe_allow_html=True)
        st.camera_input("Active Session Feed", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

def show_report():
    st.title("📊 Final Evaluation Report")
    
    with st.spinner("Generating Report..."):
        transcript_text = "\n".join([f"Q: {i['q']}\nA: {i['a']}" for i in st.session_state.transcript])
        report = call_ai([
            {"role": "system", "content": "Create a hiring report based on this transcript."},
            {"role": "user", "content": f"Transcript:\n{transcript_text}"}
        ])
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(report)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("🔄 New Interview"):
        st.session_state.clear()
        st.rerun()

# --- Main App Router ---
if st.session_state.step == 'setup':
    show_setup()
elif st.session_state.step == 'analysis':
    show_analysis()
elif st.session_state.step == 'interview':
    show_interview()
elif st.session_state.step == 'report':
    show_report()
