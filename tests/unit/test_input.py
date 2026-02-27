"""Unit tests for the input module (get_access_token, prompt_week_start_date, calculate_week_range)."""

from datetime import datetime, timedelta
from unittest import mock

import pytest

from webex_transcript_downloader import (
    AuthenticationError,
    calculate_week_range,
    get_access_token,
    prompt_week_start_date,
)


# --- Tests for get_access_token ---


def test_get_access_token_from_env():
    """Test that token is read from WEBEX_ACCESS_TOKEN env var."""
    with mock.patch.dict("os.environ", {"WEBEX_ACCESS_TOKEN": "test-token-123"}):
        token = get_access_token()
    assert token == "test-token-123"


def test_get_access_token_prompts_when_no_env():
    """Test that user is prompted when env var is not set."""
    with mock.patch.dict("os.environ", {}, clear=True):
        with mock.patch("getpass.getpass", return_value="prompted-token"):
            token = get_access_token()
    assert token == "prompted-token"


def test_get_access_token_raises_on_empty_input():
    """Test that empty token input raises AuthenticationError."""
    with mock.patch.dict("os.environ", {}, clear=True):
        with mock.patch("getpass.getpass", return_value=""):
            with pytest.raises(AuthenticationError):
                get_access_token()


def test_get_access_token_uses_getpass_for_masking():
    """Test that token input uses getpass for masking."""
    with mock.patch.dict("os.environ", {}, clear=True):
        with mock.patch("getpass.getpass", return_value="secret-token") as mock_gp:
            get_access_token()
    mock_gp.assert_called_once()


# --- Tests for prompt_week_start_date ---


def test_prompt_week_start_date_valid_yyyy_mm_dd():
    """Test parsing a valid YYYY-MM-DD date."""
    with mock.patch("builtins.input", return_value="2024-01-15"):
        result = prompt_week_start_date()
    assert result == datetime(2024, 1, 15)


def test_prompt_week_start_date_valid_mm_dd_yyyy():
    """Test parsing a valid MM/DD/YYYY date."""
    with mock.patch("builtins.input", return_value="01/15/2024"):
        result = prompt_week_start_date()
    assert result == datetime(2024, 1, 15)


def test_prompt_week_start_date_retries_on_invalid_then_succeeds():
    """Test that invalid input triggers retry and succeeds on valid input."""
    with mock.patch("builtins.input", side_effect=["not-a-date", "2024-03-01"]):
        result = prompt_week_start_date()
    assert result == datetime(2024, 3, 1)


def test_prompt_week_start_date_raises_after_3_failures():
    """Test that ValueError is raised after 3 failed attempts."""
    with mock.patch("builtins.input", side_effect=["bad1", "bad2", "bad3"]):
        with pytest.raises(ValueError, match="3 attempts"):
            prompt_week_start_date()


# --- Tests for calculate_week_range ---


def test_calculate_week_range_returns_7_days_later():
    """Test that end date is exactly 7 days after start date."""
    start = datetime(2024, 1, 15)
    end = calculate_week_range(start)
    assert end == datetime(2024, 1, 22)
    assert (end - start).days == 7


def test_calculate_week_range_preserves_time_component():
    """Test that time component is preserved in the result."""
    start = datetime(2024, 6, 10, 14, 30, 0)
    end = calculate_week_range(start)
    assert end == datetime(2024, 6, 17, 14, 30, 0)
    assert end.hour == 14
    assert end.minute == 30
