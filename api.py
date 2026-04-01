"""
API interaction module for AI Interviewer application.

Handles all communication with the Kilo AI API, including model listing and chat completions.
"""

import requests
import time
from typing import List, Dict, Any, Optional, Callable
from config import KILO_API_URL, DEFAULT_MODEL, get_api_key


def get_free_models() -> List[str]:
    """
    Retrieve a list of free AI models available from the Kilo API.

    Attempts to fetch models from the API and filters for free ones based on pricing.
    Falls back to default models if the API call fails.

    Returns:
        List[str]: List of free model IDs, with defaults as fallback.
    """
    try:
        res = requests.get(f"{KILO_API_URL}/models", timeout=10)
        if res.status_code == 200:
            data = res.json()
            models = []
            for m in data.get("data", []):
                model_id = m.get("id", "")
                pricing = m.get("pricing", {})
                is_free = float(pricing.get("prompt", 1)) == 0 and float(pricing.get("completion", 1)) == 0
                if is_free or "/free" in model_id.lower() or "free" in m.get("owned_by", "").lower():
                    models.append(model_id)
            if not models:
                models = ["kilo-auto/free", "minimax/minimax-m2.5:free"]
            return models
    except Exception:
        pass
    return ["kilo-auto/free", "minimax/minimax-m2.5:free"]


def safe_api_call(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Wrapper for API calls with error handling.

    Executes the given function with provided arguments and handles exceptions gracefully.

    Args:
        func: The function to call (should be an API function).
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        Any or None: The result of the function call, or None if an error occurred.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        import streamlit as st
        st.error(f"⚠️ Service temporarily unavailable: {str(e)}")
        return None


def call_ai(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL, retries: int = 3) -> Optional[str]:
    """
    Call the Kilo AI chat completions API.

    Sends messages to the AI model and returns the response content.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys.
        model: The model ID to use for the completion (default: DEFAULT_MODEL).
        retries: Number of retry attempts on failure (default: 3).

    Returns:
        str or None: The AI response content, or None if the call failed.
    """
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    for attempt in range(retries):
        try:
            res = requests.post(
                f"{KILO_API_URL}/chat/completions",
                headers=headers,
                json={"model": model, "messages": messages, "temperature": 0.7, "max_tokens": 1200},
                timeout=90
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                import streamlit as st
                if attempt == retries - 1:
                    st.error(f"API Error ({res.status_code}): Unable to process request")
                time.sleep(1)
        except Exception as e:
            import streamlit as st
            if attempt < retries - 1:
                time.sleep(2)
            else:
                st.error(f"Connection error: Unable to reach server")
    return None