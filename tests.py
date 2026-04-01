"""
Unit tests for AI Interviewer application.
"""

import pytest
from unittest.mock import patch, MagicMock
from utils import validate_user_info, extract_text_from_pdf, create_pdf_report
from api import get_free_models, call_ai, safe_api_call
from config import get_api_key


def test_validate_user_info():
    """Test user info validation."""
    # Valid info
    assert validate_user_info("John Doe", "john@example.com", "CAND-001", "+1234567890") == []

    # Missing fields
    assert "Name" in validate_user_info("", "john@example.com", "CAND-001", "+1234567890")
    assert "Email" in validate_user_info("John Doe", "", "CAND-001", "+1234567890")
    assert "ID" in validate_user_info("John Doe", "john@example.com", "", "+1234567890")
    assert "Phone" in validate_user_info("John Doe", "john@example.com", "CAND-001", "")


@patch('utils.PdfReader')
def test_extract_text_from_pdf(mock_pdf_reader):
    """Test PDF text extraction."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample text"
    mock_pdf_reader.return_value.pages = [mock_page]

    mock_file = MagicMock()
    result = extract_text_from_pdf(mock_file)
    assert result == "Sample text"


@patch('api.requests.get')
def test_get_free_models(mock_get):
    """Test fetching free models."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"id": "test/free", "pricing": {"prompt": 0, "completion": 0}},
            {"id": "test/paid", "pricing": {"prompt": 1, "completion": 1}}
        ]
    }
    mock_get.return_value = mock_response

    models = get_free_models()
    assert "test/free" in models
    assert "test/paid" not in models


@patch('api.requests.post')
@patch('api.get_api_key')
def test_call_ai(mock_get_key, mock_post):
    """Test AI API call."""
    mock_get_key.return_value = "test_key"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    mock_post.return_value = mock_response

    result = call_ai([{"role": "user", "content": "Hello"}])
    assert result == "Test response"


def test_safe_api_call():
    """Test safe API call wrapper."""
    def success_func():
        return "success"

    def fail_func():
        raise Exception("error")

    assert safe_api_call(success_func) == "success"
    assert safe_api_call(fail_func) is None


if __name__ == "__main__":
    pytest.main([__file__])