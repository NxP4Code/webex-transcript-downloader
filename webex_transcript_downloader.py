"""
Webex Transcript Downloader

A cross-platform, interactive command-line script that fetches meeting transcripts
from completed Webex meetings within a specified week.
"""

import getpass
import logging
import os
import re
import sys

from dotenv import load_dotenv

load_dotenv()
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when Webex API authentication fails."""

    def __init__(self, message: str = "Authentication failed. Please check your credentials and try again."):
        super().__init__(message)


class APIError(Exception):
    """Raised when a Webex API request fails."""

    def __init__(self, message: str = "Webex API request failed."):
        super().__init__(message)





@dataclass
class Meeting:
    """Represents a completed Webex meeting with transcript availability."""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    has_transcript: bool


@dataclass
class DownloadResult:
    """Tracks the outcome of a transcript download attempt."""
    meeting: Meeting
    success: bool
    error_message: Optional[str] = None
    filename: Optional[str] = None


@dataclass
class Summary:
    """Final statistics for a transcript download session."""
    total_meetings: int
    transcripts_downloaded: int
    transcripts_unavailable: int
    failed_downloads: int
    failed_meetings: List[Tuple[str, str]]  # (meeting_title, error_message)


def get_access_token() -> str:
    """
    Gets Webex personal access token from environment variable or user prompt.
    Checks WEBEX_ACCESS_TOKEN env var first, then prompts interactively.
    Returns: Access token string
    """
    token = os.environ.get("WEBEX_ACCESS_TOKEN", "").strip()
    if token:
        print("Using access token from WEBEX_ACCESS_TOKEN environment variable.")
        return token
    print("No WEBEX_ACCESS_TOKEN found in environment.")
    print("Get a personal access token from https://developer.webex.com")
    token = getpass.getpass("Enter your Webex personal access token: ").strip()
    if not token:
        raise AuthenticationError("No access token provided.")
    return token


def prompt_week_start_date() -> datetime:
    """
    Prompts user for week start date with validation.
    Supports formats: YYYY-MM-DD, MM/DD/YYYY, ISO 8601.
    Retries up to 3 times on invalid input.
    Returns: datetime object representing the start date
    Raises: ValueError if date format is invalid after retries
    """
    date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]
    max_retries = 3

    for attempt in range(max_retries):
        date_str = input("Enter week start date (YYYY-MM-DD): ").strip()
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        print("Invalid date format. Please enter date as YYYY-MM-DD (e.g., 2024-01-15)")

    raise ValueError("Failed to parse date after 3 attempts.")


def calculate_week_range(start_date: datetime) -> datetime:
    """
    Calculate end date as exactly 7 days after start date.
    Args: start_date - datetime representing the week start
    Returns: datetime representing the end date (7 days later)
    """
    return start_date + timedelta(days=7)

def validate_token(token: str) -> str:
    """
    Validates a Webex personal access token by calling /v1/people/me.
    Args:
        token: Webex personal access token
    Returns: Display name of the authenticated user
    Raises: AuthenticationError if token is invalid or request fails
    """
    url = f"{WEBEX_BASE_URL}/v1/people/me"
    logger.info("Validating access token...")

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        name = data.get("displayName", "Unknown")
        logger.info("Token validated for user: %s", name)
        return name
    except requests.exceptions.HTTPError as e:
        logger.error("Token validation failed: HTTP %s", e.response.status_code if e.response is not None else "unknown")
        raise AuthenticationError("Invalid access token. Please get a new one from https://developer.webex.com") from e
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection error during token validation: %s", e)
        raise AuthenticationError("Unable to connect to Webex API. Please check your network connection.") from e
    except requests.exceptions.Timeout as e:
        logger.error("Timeout during token validation: %s", e)
        raise AuthenticationError("Token validation timed out. Please try again.") from e
    except requests.exceptions.RequestException as e:
        logger.error("Unexpected error during token validation: %s", e)
        raise AuthenticationError(f"Token validation failed: {e}") from e

WEBEX_BASE_URL = "https://webexapis.com"




def fetch_available_transcripts(token: str, start_date: datetime, end_date: datetime) -> list:
    """
    Fetches all available transcripts for a date range from /v1/meetingTranscripts.
    This includes transcripts from meetings you hosted AND attended.
    Returns: list of dicts with keys: meetingId, meetingTopic, txtDownloadLink, startTime
    Raises: APIError on request failures
    """
    url = f"{WEBEX_BASE_URL}/v1/meetingTranscripts"
    params = {
        "meetingStartTimeFrom": start_date.strftime("%Y-%m-%dT00:00:00Z"),
        "meetingStartTimeTo": end_date.strftime("%Y-%m-%dT23:59:59Z"),
    }
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("Fetching available transcripts for date range")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error("Failed to fetch transcripts: HTTP %s", e.response.status_code if e.response is not None else "unknown")
        raise APIError(f"Failed to fetch transcripts: {e}") from e
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching transcripts: %s", e)
        raise APIError(f"Failed to fetch transcripts: {e}") from e

    data = response.json()
    items = data.get("items", [])
    transcripts = []
    for item in items:
        start_str = item.get("startTime", "")
        try:
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00")) if start_str else start_date
        except ValueError:
            start_time = start_date
        transcripts.append({
            "meetingId": item.get("meetingId", ""),
            "meetingTopic": item.get("meetingTopic", "Untitled Meeting"),
            "txtDownloadLink": item.get("txtDownloadLink", ""),
            "startTime": start_time,
        })

    logger.info("Found %d available transcript(s).", len(transcripts))
    return transcripts


def download_transcript(token: str, download_url: str) -> str:
    """
    Downloads transcript content from a direct download URL.
    Args:
        token: Webex API access token
        download_url: The txtDownloadLink URL from the transcripts API
    Returns: Transcript text content
    Raises: APIError on request failures
    """
    headers = {"Authorization": f"Bearer {token}"}

    logger.info("Downloading transcript from %s", download_url)

    try:
        response = requests.get(download_url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error("Failed to download transcript: HTTP %s", e.response.status_code if e.response is not None else "unknown")
        raise APIError(f"Failed to download transcript: {e}") from e
    except requests.exceptions.RequestException as e:
        logger.error("Error downloading transcript: %s", e)
        raise APIError(f"Failed to download transcript: {e}") from e

    logger.info("Successfully downloaded transcript")
    return response.text


def sanitize_filename(meeting_title: str, meeting_date: datetime) -> str:
    """
    Creates a safe filename from meeting title and date.
    Removes invalid characters for both Windows and Mac.
    Returns: Sanitized filename string in format YYYY-MM-DD_sanitized_title.txt
    """
    date_prefix = meeting_date.strftime("%Y-%m-%d")
    sanitized_title = re.sub(r'[<>:"/\\|?*]', "_", meeting_title)
    filename = f"{date_prefix}_{sanitized_title}.txt"
    if len(filename) > 255:
        # Preserve the .txt extension and date prefix within the 255 limit
        max_title_len = 255 - len(date_prefix) - len("_.txt")
        sanitized_title = sanitized_title[:max_title_len]
        filename = f"{date_prefix}_{sanitized_title}.txt"
    return filename


def save_transcript(content: str, filename: str, output_dir: Path) -> None:
    """
    Saves transcript content to a file.
    Args:
        content: Transcript text content
        filename: Sanitized filename for the transcript
        output_dir: Directory to save the transcript in
    Raises: IOError if file cannot be written
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / filename
        file_path.write_text(content, encoding="utf-8")
        logger.info("Saved transcript to %s", file_path)
    except OSError as e:
        logger.error("Failed to save transcript to %s: %s", filename, e)
        raise IOError(f"Failed to save transcript to '{filename}': {e}") from e


def display_progress(current: int, total: int, title: str) -> None:
    """
    Display progress information for the current meeting being processed.
    Args:
        current: Current meeting number (1-based)
        total: Total number of meetings
        title: Title of the meeting being processed
    """
    print(f"Processing [{current}/{total}]: {title}")


def process_transcripts(
    transcripts: list,
    token: str,
    output_dir: Path,
) -> List[DownloadResult]:
    """
    Download and save each available transcript.
    Args:
        transcripts: list of dicts from fetch_available_transcripts
        token: Webex API access token
        output_dir: Directory to save transcript files
    Returns: List of DownloadResult objects
    """
    results: List[DownloadResult] = []
    total = len(transcripts)
    for i, t in enumerate(transcripts):
        title = t["meetingTopic"]
        display_progress(i + 1, total, title)
        meeting = Meeting(
            id=t["meetingId"],
            title=title,
            start_time=t["startTime"],
            end_time=t["startTime"],
            has_transcript=True,
        )
        try:
            content = download_transcript(token, t["txtDownloadLink"])
            filename = sanitize_filename(title, t["startTime"])
            save_transcript(content, filename, output_dir)
            print(f"  Downloaded: {filename}")
            results.append(DownloadResult(meeting=meeting, success=True, filename=filename))
        except (APIError, IOError) as e:
            print(f"  Failed: {e}")
            results.append(DownloadResult(meeting=meeting, success=False, error_message=str(e)))
    return results


def display_summary(results: List[DownloadResult], total_meetings: int) -> None:
    """
    Display a summary of the download session.
    Args:
        results: List of DownloadResult objects
        total_meetings: Total number of meetings found
    """
    downloaded = sum(1 for r in results if r.success)
    unavailable = sum(1 for r in results if not r.success and r.error_message == "No transcript available")
    failed = sum(1 for r in results if not r.success and r.error_message != "No transcript available")

    print("\n" + "=" * 40)
    print("Summary")
    print("=" * 40)
    print(f"Total meetings found: {total_meetings}")
    print(f"Transcripts downloaded: {downloaded}")
    print(f"Transcripts unavailable: {unavailable}")
    print(f"Failed downloads: {failed}")

    if failed > 0:
        print("\nFailed downloads:")
        for r in results:
            if not r.success and r.error_message != "No transcript available":
                print(f"  - {r.meeting.title}: {r.error_message}")




def main() -> None:
    """Main entry point that orchestrates the entire workflow."""
    print("Webex Transcript Downloader")
    print("=" * 40)

    try:
        token = get_access_token()
        name = validate_token(token)
        print(f"Authenticated as: {name}\n")

        week_start = prompt_week_start_date()
        week_end = calculate_week_range(week_start)

        print(f"\nFetching transcripts from {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}...")
        transcripts = fetch_available_transcripts(token, week_start, week_end)
        print(f"Found {len(transcripts)} transcript(s) available.\n")

        if not transcripts:
            print("No transcripts found for the specified week.")
            return

        output_dir = Path("transcripts")
        results = process_transcripts(transcripts, token, output_dir)
        display_summary(results, len(transcripts))

    except (AuthenticationError, APIError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

def setup_logging() -> None:
    """Configure logging to file for debugging."""
    file_handler = logging.FileHandler("webex_transcript_downloader.log")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)



if __name__ == "__main__":
    setup_logging()
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unhandled error")
        print(f"Unexpected error: {e}")
        sys.exit(1)
