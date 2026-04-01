"""
Configuration module for AI Interviewer application.

Handles environment variables, API keys, and application constants.
"""

import os
import base64
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Application constants
LOGO_PATH: str = "manver-logo.png"
LOGO_BASE64: str = ""

try:
    with open(LOGO_PATH, "rb") as f:
        LOGO_BASE64 = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    LOGO_BASE64 = ""  # Fallback if logo file is missing

# API configuration
KILO_API_URL: str = "https://api.kilo.ai/api/gateway"
DEFAULT_MODEL: str = "kilo-auto/free"


def get_api_key() -> Optional[str]:
    """
    Retrieve the Kilo AI API key from environment variables.

    Checks both VITE_KILO_API_KEY and KILO_API_KEY environment variables.

    Returns:
        str or None: The API key if found, None otherwise.
    """
    return os.getenv("VITE_KILO_API_KEY") or os.getenv("KILO_API_KEY")