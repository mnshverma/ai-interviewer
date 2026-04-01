"""
Utility functions for AI Interviewer application.

Contains helper functions for PDF processing, loading states, and data validation.
"""

import streamlit as st
from pypdf import PdfReader
from fpdf import FPDF
import tempfile
import os
from typing import Dict, Any, Optional, Union
from io import BytesIO


def show_loading_overlay(message: str = "Loading...") -> None:
    """
    Display a full-screen loading overlay with a spinner and message.

    Args:
        message: The message to display in the loading overlay.
    """
    st.markdown(f'''
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">{message}</p>
        </div>
    </div>
    <script>document.body.style.overflow = 'hidden';</script>
    ''', unsafe_allow_html=True)


def hide_loading_overlay() -> None:
    """
    Hide the loading overlay and restore normal page scrolling.
    """
    st.markdown("""
    <script>
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    document.body.style.overflow = 'auto';
    </script>
    """, unsafe_allow_html=True)


def extract_text_from_pdf(file: Any) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file: The uploaded PDF file object.

    Returns:
        str: The extracted text from the PDF, or empty string on error.
    """
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""


def create_pdf_report(info: Dict[str, str], evaluation: Optional[str], transcript: str, photo_bytes: Optional[BytesIO] = None) -> bytes:
    """
    Generate a PDF report for the interview assessment.

    Args:
        info: Dictionary containing candidate information (name, id, email, phone).
        evaluation: The AI evaluation text.
        transcript: The full interview transcript.
        photo_bytes: Optional photo data for inclusion in the report.

    Returns:
        bytes: The generated PDF as bytes.
    """
    pdf = FPDF()
    pdf.add_page()

    is_pass = evaluation and "PASS" in str(evaluation).upper()
    decision_color = (16, 185, 129) if is_pass else (239, 68, 68)
    decision_text = "FINAL RESULT: PASS" if is_pass else "FINAL RESULT: FAIL"

    pdf.set_line_width(0.3)
    pdf.rect(5, 5, 200, 287)

    pdf.set_fill_color(10, 14, 23)
    pdf.rect(5, 5, 200, 45, 'F')

    from config import LOGO_PATH
    try:
        pdf.image(LOGO_PATH, 10, 10, 35, 35)
    except:
        pass

    if photo_bytes:
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
    pdf.cell(100, 6, f"TIME: {st.session_state.get('interview_time', 'N/A')}", 0, 1)

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
    pdf.multi_cell(0, 7, str(evaluation or "").encode('latin-1', 'replace').decode('latin-1'))

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


def validate_user_info(name: str, email: str, candidate_id: str, phone: str) -> list[str]:
    """
    Validate user input fields for required information.

    Args:
        name: Candidate's full name.
        email: Candidate's email address.
        candidate_id: Candidate's unique ID.
        phone: Candidate's phone number.

    Returns:
        list[str]: List of missing required fields.
    """
    missing = []
    if not name.strip():
        missing.append("Name")
    if not email.strip():
        missing.append("Email")
    if not candidate_id.strip():
        missing.append("ID")
    if not phone.strip():
        missing.append("Phone")
    return missing