"""
AI Interviewer Application - Main Entry Point

A Streamlit-based application for conducting AI-powered technical interviews.
"""

import streamlit as st
from config import LOGO_PATH
from state import initialize_session_state
from ui import render_header, show_setup, show_analysis, show_interview, show_report

st.set_page_config(
    page_title="MANVER AI INTERVIEWER",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
initialize_session_state()

# CSS Styling (Embedded for now - could be moved to separate file later)
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

    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(3, 7, 18, 0.9);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        animation: fadeIn 0.3s ease-out;
    }

    .loading-content {
        text-align: center;
        padding: 2rem;
        background: var(--bg-glass);
        border-radius: 20px;
        border: 1px solid var(--border-glass);
        box-shadow: var(--shadow-premium);
    }

    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid var(--border-glass);
        border-top: 4px solid var(--accent-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# Main application routing
step = st.session_state.get('step', 'setup')

# Only show session header if user is identified
if step in ['interview', 'report'] and st.session_state.get('user_info'):
    render_header()

if step == 'setup':
    show_setup()
elif step == 'analysis':
    show_analysis()
elif step == 'interview':
    show_interview()
elif step == 'report':
    show_report()