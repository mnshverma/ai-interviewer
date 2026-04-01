"""
UI rendering module for AI Interviewer application.

Contains all Streamlit UI components and rendering functions.
"""

import streamlit as st
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from eye_tracking import EyeTracker
from api import safe_api_call, call_ai
from utils import extract_text_from_pdf, show_loading_overlay, hide_loading_overlay, create_pdf_report, validate_user_info
from state import get_user_info, update_user_info
from config import LOGO_BASE64


def render_branding() -> None:
    """
    Render the ultra-premium branding header with logo and tagline.
    """
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


def render_step_progress() -> None:
    """
    Render a clean wizard-style progress indicator for the 4-step workflow.
    """
    steps = [
        {"label": "Setup", "step": "setup"},
        {"label": "Analysis", "step": "analysis"},
        {"label": "Interview", "step": "interview"},
        {"label": "Report", "step": "report"}
    ]

    current_step = st.session_state.get('step', 'setup')
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


def render_header() -> None:
    """
    Render a minimal header showing candidate info during interview and report steps.
    """
    if 'user_info' not in st.session_state or not st.session_state.user_info.get("name"):
        return

    step = st.session_state.get('step', 'setup')
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


@st.dialog("Confirm Submission")
def confirm_submission() -> None:
    """
    Display a confirmation dialog before submitting the interview.
    """
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


def show_setup() -> None:
    """
    Render the setup step: User details form and document upload/analysis.
    """
    render_branding()
    render_step_progress()

    st.markdown("<h1>Your Details</h1>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.text_input("Full Name *", key="reg_name", placeholder="John Doe")
        st.text_input("Email *", key="reg_email", placeholder="john@example.com")
    with c2:
        st.text_input("Candidate ID *", key="reg_id", placeholder="CAND-001")
        st.text_input("Phone *", key="reg_phone", placeholder="+91 XXXX XXXX")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Resume or Job Description")

    input_type = st.radio(
        "Choose:",
        ["Upload Resume (PDF)", "Paste Job Description"],
        horizontal=True,
        label_visibility="collapsed"
    )

    uploaded_file = None
    jd_text = ""

    if input_type == "Upload Resume (PDF)":
        uploaded_file = st.file_uploader("Upload", type=['pdf'], label_visibility="collapsed")
        if uploaded_file:
            st.success(f"✓ {uploaded_file.name}")
    else:
        jd_text = st.text_area("Job Description", height=120, placeholder="Paste job description...", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Continue", type="primary", use_container_width=True):
        v_name = str(st.session_state.get("reg_name", "")).strip()
        v_id = str(st.session_state.get("reg_id", "")).strip()
        v_email = str(st.session_state.get("reg_email", "")).strip()
        v_phone = str(st.session_state.get("reg_phone", "")).strip()

        missing = validate_user_info(v_name, v_email, v_id, v_phone)

        if missing:
            st.error(f"Please fill: {', '.join(missing)}")
        elif input_type == "Upload Resume (PDF)" and not uploaded_file:
            st.error("Please upload your resume")
        elif input_type == "Paste Job Description" and not jd_text.strip():
            st.error("Please paste the job description")
        else:
            update_user_info(v_name, v_email, v_id, v_phone)

            show_loading_overlay("Analyzing...")

            if input_type == "Upload Resume (PDF)":
                input_content = extract_text_from_pdf(uploaded_file)
                prompt_msg = "Analyze this resume and identify key skills, experience, and qualifications."
            else:
                input_content = jd_text
                prompt_msg = "Analyze this job description and identify key skills, requirements, and qualifications. NO LINKS."

            model = st.session_state.get("available_models", ["kilo-auto/free"])[0]
            res = safe_api_call(call_ai, [{"role": "system", "content": prompt_msg}, {"role": "user", "content": input_content}], model=model)

            hide_loading_overlay()

            if res:
                st.session_state.analysis = res
                st.session_state.step = 'analysis'
                st.rerun()


def show_analysis() -> None:
    """
    Render the analysis step: Display AI analysis and proceed to interview.
    """
    render_branding()
    render_step_progress()

    st.markdown("<h1>Analysis</h1>", unsafe_allow_html=True)

    info = get_user_info()
    st.markdown(f"""
        <div class="wizard-card">
            <h3 style="margin-bottom: 1rem;">Your Profile</h3>
            <p style="color: var(--text-secondary);">{info['name']} | {info['email']} | {info['id']}</p>
        </div>
    """, unsafe_allow_html=True)

    analysis_text = st.session_state.get('analysis', '').strip()
    if analysis_text:
        with st.expander("View AI Analysis", expanded=False):
            st.markdown(analysis_text)
    else:
        st.warning("Analysis not available. Please go back.")

    st.markdown("<br>", unsafe_allow_html=True)

    if not analysis_text:
        st.button("Continue", type="primary", use_container_width=True, disabled=True)
    elif st.button("Continue", type="primary", use_container_width=True):
        show_loading_overlay("Preparing...")

        prompt = "Generate 8 technical interview questions based on skills. One per line."
        text = safe_api_call(call_ai, [{"role": "system", "content": prompt}, {"role": "user", "content": analysis_text}])

        hide_loading_overlay()

        if text:
            questions = [q.strip() for q in text.split('\n') if len(q.strip()) > 15][:8]
            if len(questions) < 5:
                questions = [
                    "Describe your experience with system design.",
                    "How do you debug production issues?",
                    "Explain your performance optimization strategy.",
                    "What is your experience with cloud services?",
                    "How do you ensure code quality?",
                    "Describe a challenging problem you solved.",
                    "How do you stay updated with tech?",
                    "Explain security best practices."
                ][:8]
            st.session_state.questions = questions
            st.session_state.answers = [""] * len(questions)
            st.session_state.current_q = 0
            st.session_state.step = 'interview'
            st.rerun()


@st.fragment
def interview_content() -> None:
    """
    Render the interview content: Question display and answer input.
    """
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

    # Proctoring section (Optional)
    if st.session_state.get('eye_tracking_active'):
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


def show_interview() -> None:
    """
    Render the interview step with question navigation and optional proctoring.
    """
    render_step_progress()
    interview_content()


def show_report() -> None:
    """
    Render the final report step with evaluation and PDF download.
    """
    render_step_progress()

    info = get_user_info()

    show_loading_overlay("Evaluating your performance...")

    transcript = ""
    for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
        transcript += f"Q{i+1}: {q}\nA: {a}\n\n"

    res = safe_api_call(call_ai, [
        {"role": "system", "content": "You are an expert technical interviewer. Evaluate the candidate's interview responses. You MUST START your response with either 'RESULT: PASS' or 'RESULT: FAIL' based on the overall quality of answers, then provide detailed feedback including strengths, areas for improvement, and a final recommendation."},
        {"role": "user", "content": f"Candidate: {info.get('name', 'N/A')}\nID: {info.get('id', 'N/A')}\nEmail: {info.get('email', 'N/A')}\nDate: {st.session_state.interview_time}\n\nInterview Transcript:\n{transcript}"}
    ])

    hide_loading_overlay()

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

    # Metrics row (only if eye tracking was active)
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
            from state import reset_session_state
            reset_session_state()
            st.rerun()