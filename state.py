"""
Session state management for AI Interviewer application.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st
from datetime import datetime
from eye_tracking import EyeTracker
from api import safe_api_call, get_free_models
from typing import Dict, List, Any, Optional


def initialize_session_state() -> None:
    """
    Initialize all required session state variables with default values.

    This function sets up the initial state for the application, including
    device testing, user information, interview data, and eye tracking.
    """
    # Available models
    if 'available_models' not in st.session_state:
        st.session_state.available_models = safe_api_call(get_free_models) or ["kilo-auto/free"]

    # Device testing state
    if 'device_test_done' not in st.session_state:
        st.session_state.device_test_done = False
    if 'device_permissions_granted' not in st.session_state:
        st.session_state.device_permissions_granted = False
    if 'device_test_step' not in st.session_state:
        st.session_state.device_test_step = 0

    # User information
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {"name": "", "email": "", "phone": "", "id": ""}

    # Registration form fields
    if 'reg_name' not in st.session_state:
        st.session_state.reg_name = ""
    if 'reg_email' not in st.session_state:
        st.session_state.reg_email = ""
    if 'reg_id' not in st.session_state:
        st.session_state.reg_id = ""
    if 'reg_phone' not in st.session_state:
        st.session_state.reg_phone = ""

    # Interview data
    if 'step' not in st.session_state:
        st.session_state.step = 'setup'
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

    # Media verification
    if 'mic_verified' not in st.session_state:
        st.session_state.mic_verified = False
    if 'photo_verified' not in st.session_state:
        st.session_state.photo_verified = False

    # Eye tracking (made optional)
    if 'eye_tracker' not in st.session_state:
        st.session_state.eye_tracker = EyeTracker()
    if 'eye_calibration_done' not in st.session_state:
        st.session_state.eye_calibration_done = False
    if 'eye_tracking_active' not in st.session_state:
        st.session_state.eye_tracking_active = False  # Default to inactive
    if 'eye_tracking_report' not in st.session_state:
        st.session_state.eye_tracking_report = None

    # Interview termination
    if 'interview_terminated' not in st.session_state:
        st.session_state.interview_terminated = False

    # Ensure user_info fields exist
    if 'user_info' in st.session_state:
        for key in ["name", "email", "phone", "id"]:
            if key not in st.session_state.user_info:
                st.session_state.user_info[key] = ""


def reset_session_state() -> None:
    """
    Reset all session state variables to start a new interview session.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()


def get_user_info() -> Dict[str, str]:
    """
    Get the current user information from session state.

    Returns:
        Dict[str, str]: Dictionary containing user information.
    """
    return st.session_state.get('user_info', {"name": "", "email": "", "phone": "", "id": ""})


def update_user_info(name: str, email: str, candidate_id: str, phone: str) -> None:
    """
    Update user information in session state.

    Args:
        name: Candidate's full name.
        email: Candidate's email address.
        candidate_id: Candidate's unique ID.
        phone: Candidate's phone number.
    """
    st.session_state.user_info = {
        "name": name,
        "id": candidate_id,
        "email": email,
        "phone": phone
    }
    st.session_state.interview_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")