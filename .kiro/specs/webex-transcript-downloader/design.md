# Design Document: Webex Transcript Downloader

## Overview

The Webex Transcript Downloader is a cross-platform, interactive command-line script that enables users to download meeting transcripts from completed Webex meetings within a specified week. The script provides a simple, user-friendly interface that prompts for credentials and week selection, then automatically fetches and saves available transcripts.

### Key Design Goals

- **Simplicity**: Single-file script with minimal dependencies
- **Cross-platform**: Works identically on Windows and macOS
- **Interactive**: Guided prompts for all user input
- **Robust**: Graceful error handling and clear progress feedback
- **MVP Scope**: Focus on completed meetings only

### Technology Stack

- **Language**: Python 3.8+ (excellent cross-platform support, rich ecosystem)
- **HTTP Client**: `requests` library for Webex API interactions
- **Input Handling**: `getpass` for secure password input
- **Date Handling**: `datetime` for date parsing and week range calculation
- **File Operations**: `pathlib` for cross-platform path handling

## Architecture

### High-Level Flow

```
┌─────────────────┐
│  Start Script   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt for      │
│ Credentials     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Authenticate    │
│ with Webex API  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt for      │
│ Week Start Date │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Calculate       │
│ Week Range      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fetch Completed │
│ Meetings        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ For Each        │
│ Meeting:        │
│ - Check if      │
│   transcript    │
│   available     │
│ - Download      │
│ - Save to file  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Summary │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      Exit       │
└─────────────────┘
```

### Component Architecture

The script follows a procedural design with clear separation of concerns:

1. **Input Module**: Handles user prompts and validation
2. **Authentication Module**: Manages Webex API authentication
3. **API Client Module**: Encapsulates Webex API interactions
4. **File Handler Module**: Manages transcript file operations
5. **Main Orchestrator**: Coordinates the overall workflow

## Components and Interfaces

### 1. Input Module

**Responsibilities**:

- Prompt for username and password
- Prompt for week start date
- Validate date format
- Mask password input

**Key Functions**:

```python
def prompt_credentials() -> tuple[str, str]:
    """
    Prompts user for Webex credentials.
    Returns: (username, password)
    """

def prompt_week_start_date() -> datetime:
    """
    Prompts user for week start date with validation.
    Returns: datetime object representing the start date
    Raises: ValueError if date format is invalid after retries
    """
```

### 2. Authentication Module

**Responsibilities**:

- Authenticate with Webex API using credentials
- Obtain and manage access token
- Handle authentication errors

**Key Functions**:

```python
def authenticate(username: str, password: str) -> str:
    """
    Authenticates with Webex API.
    Returns: Access token string
    Raises: AuthenticationError if credentials are invalid
    """
```

**Webex API Authentication**:

- Uses OAuth 2.0 or Basic Authentication (depending on Webex API requirements)
- Endpoint: `https://webexapis.com/v1/authorize` or similar
- Returns bearer token for subsequent API calls

### 3. API Client Module

**Responsibilities**:

- Query meetings within date range
- Fetch transcript availability
- Download transcript content
- Handle API errors and rate limiting

**Key Functions**:

```python
def fetch_meetings(token: str, start_date: datetime, end_date: datetime) -> list[Meeting]:
    """
    Fetches completed meetings within the specified date range.
    Returns: List of Meeting objects
    Raises: APIError if request fails
    """

def download_transcript(token: str, meeting_id: str) -> str:
    """
    Downloads transcript content for a specific meeting.
    Returns: Transcript text content
    Raises: TranscriptNotAvailableError, APIError
    """
```

**Webex API Endpoints**:

- List meetings: `GET /v1/meetings?from={start}&to={end}&state=ended`
- Get transcript: `GET /v1/meetings/{meetingId}/transcripts`

### 4. File Handler Module

**Responsibilities**:

- Sanitize filenames for cross-platform compatibility
- Save transcripts to local files
- Handle file I/O errors

**Key Functions**:

```python
def sanitize_filename(meeting_title: str, meeting_date: datetime) -> str:
    """
    Creates a safe filename from meeting title and date.
    Removes invalid characters for both Windows and Mac.
    Returns: Sanitized filename string
    """

def save_transcript(content: str, filename: str, output_dir: Path) -> None:
    """
    Saves transcript content to a file.
    Raises: IOError if file cannot be written
    """
```

**Filename Sanitization**:

- Remove/replace characters: `< > : " / \ | ? *`
- Limit filename length to 255 characters
- Format: `{YYYY-MM-DD}_{sanitized_title}.txt`

### 5. Main Orchestrator

**Responsibilities**:

- Coordinate overall workflow
- Display progress messages
- Handle errors gracefully
- Generate final summary

**Key Function**:

```python
def main() -> None:
    """
    Main entry point that orchestrates the entire workflow.
    """
```

## Data Models

### Meeting

```python
@dataclass
class Meeting:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    has_transcript: bool
```

### DownloadResult

```python
@dataclass
class DownloadResult:
    meeting: Meeting
    success: bool
    error_message: Optional[str] = None
    filename: Optional[str] = None
```

### Summary

```python
@dataclass
class Summary:
    total_meetings: int
    transcripts_downloaded: int
    transcripts_unavailable: int
    failed_downloads: int
    failed_meetings: list[tuple[str, str]]  # (meeting_title, error_message)
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: Week Range Calculation

_For any_ valid start date, calculating the week range should produce an end date that is exactly 7 days (168 hours) after the start date.

**Validates: Requirements 3.3**

### Property 2: Date Format Validation

_For any_ string input, the date validation function should accept valid date formats (ISO 8601, common formats like YYYY-MM-DD, MM/DD/YYYY) and reject invalid formats with an appropriate error.

**Validates: Requirements 3.4, 3.5**

### Property 3: Filename Sanitization

_For any_ meeting title and date, the generated filename should not contain any invalid filesystem characters (`< > : " / \ | ? *`) and should include both the date in YYYY-MM-DD format and a sanitized version of the title.

**Validates: Requirements 5.2, 5.3**

### Property 4: Cross-Platform Path Handling

_For any_ file path operation, using pathlib should produce valid paths on both Windows (backslash separators) and Unix-like systems (forward slash separators) without manual separator handling.

**Validates: Requirements 1.3**

### Property 5: Authentication Error Handling

_For any_ authentication attempt, if the credentials are invalid, the system should raise an AuthenticationError with a descriptive message and not proceed to subsequent operations.

**Validates: Requirements 2.5**

### Property 6: Meeting Filtering

_For any_ list of meetings returned from the API, the filtered results should only include meetings where the state is "ended" or "completed", excluding any ongoing or scheduled meetings.

**Validates: Requirements 4.3**

### Property 7: Meeting Metadata Completeness

_For any_ meeting object parsed from the API response, it should contain all required fields: id, title, start_time, end_time, and has_transcript flag.

**Validates: Requirements 4.2**

### Property 8: API Query Parameters

_For any_ week range with start and end dates, the API query should include both dates as parameters and request only meetings with state="ended".

**Validates: Requirements 4.1**

### Property 9: Download Attempt Coverage

_For any_ list of meetings, download attempts should be made for exactly those meetings where has_transcript is True, and no download attempts should be made for meetings where has_transcript is False.

**Validates: Requirements 5.1**

### Property 10: Error Resilience

_For any_ sequence of meetings being processed, if one meeting's transcript download fails or is unavailable, the script should continue processing all remaining meetings in the sequence.

**Validates: Requirements 5.4, 6.2**

### Property 11: Summary Statistics Accuracy

_For any_ completed download session, the summary should accurately reflect: total_meetings = (transcripts_downloaded + transcripts_unavailable + failed_downloads), and each count should match the actual number of meetings in each category.

**Validates: Requirements 5.5, 6.3, 7.4**

### Property 12: Progress Information Completeness

_For any_ meeting being processed, the progress display should include the current meeting number, total meeting count, and the meeting title being processed.

**Validates: Requirements 7.1, 7.2, 7.3**

### Property 13: Meeting Count Accuracy

_For any_ API response containing meetings, the displayed count of completed meetings should equal the length of the filtered meeting list.

**Validates: Requirements 4.5**

## Error Handling

The script implements a layered error handling strategy to provide clear feedback and graceful degradation:

### Error Categories

#### 1. Authentication Errors

**Scenarios**:

- Invalid credentials
- Network connectivity issues during authentication
- Expired or revoked tokens

**Handling**:

- Display clear error message indicating authentication failure
- Exit with non-zero status code
- Do not retry automatically (user must re-run with correct credentials)

**Example Message**: `"Authentication failed: Invalid username or password. Please check your credentials and try again."`

#### 2. Input Validation Errors

**Scenarios**:

- Invalid date format
- Date parsing failures

**Handling**:

- Display error message with expected format
- Re-prompt user for input (up to 3 attempts)
- Exit if validation fails after maximum attempts

**Example Message**: `"Invalid date format. Please enter date as YYYY-MM-DD (e.g., 2024-01-15)"`

#### 3. API Request Errors

**Scenarios**:

- Network timeouts
- API rate limiting (429 status)
- Server errors (5xx status)
- Invalid API responses

**Handling**:

- For rate limiting: Wait and retry with exponential backoff (max 3 retries)
- For server errors: Display error and exit
- For network errors: Display error and exit
- Log full error details for debugging

**Example Message**: `"Failed to fetch meetings from Webex API: Connection timeout. Please check your network connection."`

#### 4. Transcript Download Errors

**Scenarios**:

- Transcript not available despite flag indicating availability
- Network errors during download
- Malformed transcript data

**Handling**:

- Log error with meeting details
- Continue processing remaining meetings
- Include in failed downloads count
- Display in final summary

**Example Message**: `"Failed to download transcript for 'Team Standup' (2024-01-15): Transcript not found"`

#### 5. File I/O Errors

**Scenarios**:

- Insufficient disk space
- Permission denied for output directory
- Invalid characters in filename (despite sanitization)

**Handling**:

- Display error with specific file details
- Continue processing remaining meetings
- Include in failed downloads count

**Example Message**: `"Failed to save transcript to 'output/2024-01-15_meeting.txt': Permission denied"`

### Error Recovery Strategy

```python
# Pseudo-code for error handling pattern
def main():
    try:
        # Critical operations that should stop execution
        credentials = prompt_credentials()
        token = authenticate(credentials)  # Raises AuthenticationError
        week_start = prompt_week_start_date()  # Raises ValidationError after retries

        # Operations that should continue despite individual failures
        meetings = fetch_meetings(token, week_start)  # Raises APIError
        results = []

        for meeting in meetings:
            try:
                # Individual meeting processing - failures don't stop the loop
                if meeting.has_transcript:
                    transcript = download_transcript(token, meeting.id)
                    save_transcript(transcript, meeting)
                    results.append(DownloadResult(meeting, success=True))
            except (TranscriptError, IOError) as e:
                # Log and continue
                results.append(DownloadResult(meeting, success=False, error=str(e)))

        display_summary(results)

    except (AuthenticationError, ValidationError, APIError) as e:
        print(f"Error: {e}")
        sys.exit(1)
```

### Logging

- Log all API requests and responses (excluding sensitive data)
- Log all errors with full stack traces to a log file
- Console output shows user-friendly messages only
- Log file location: `./webex_transcript_downloader.log`

## Testing Strategy

### Overview

The testing strategy employs a dual approach combining unit tests for specific scenarios and property-based tests for universal behaviors. This ensures both concrete correctness and comprehensive input coverage.

### Property-Based Testing

**Framework**: `hypothesis` (Python's leading property-based testing library)

**Configuration**:

- Minimum 100 iterations per property test
- Each test tagged with feature name and property reference
- Custom generators for domain-specific types (dates, meeting objects, filenames)

**Property Test Implementation**:

Each correctness property from the design document will be implemented as a property-based test:

```python
from hypothesis import given, strategies as st
import hypothesis

# Configure hypothesis
hypothesis.settings.register_profile("ci", max_examples=100)
hypothesis.settings.load_profile("ci")

# Example property test
@given(start_date=st.datetimes())
def test_week_range_calculation(start_date):
    """
    Feature: webex-transcript-downloader, Property 1:
    For any valid start date, calculating the week range should produce
    an end date that is exactly 7 days (168 hours) after the start date.
    """
    end_date = calculate_week_range(start_date)
    delta = end_date - start_date
    assert delta.days == 7
    assert delta.total_seconds() == 7 * 24 * 60 * 60

@given(meeting_title=st.text(), meeting_date=st.datetimes())
def test_filename_sanitization(meeting_title, meeting_date):
    """
    Feature: webex-transcript-downloader, Property 3:
    For any meeting title and date, the generated filename should not
    contain any invalid filesystem characters.
    """
    filename = sanitize_filename(meeting_title, meeting_date)
    invalid_chars = '<>:"/\\|?*'
    assert not any(char in filename for char in invalid_chars)
    assert meeting_date.strftime('%Y-%m-%d') in filename

@given(meetings=st.lists(st.builds(Meeting)))
def test_download_attempt_coverage(meetings):
    """
    Feature: webex-transcript-downloader, Property 9:
    For any list of meetings, download attempts should be made for exactly
    those meetings where has_transcript is True.
    """
    attempted_downloads = []

    def mock_download(meeting_id):
        attempted_downloads.append(meeting_id)
        return "transcript content"

    process_meetings(meetings, download_func=mock_download)

    expected_downloads = [m.id for m in meetings if m.has_transcript]
    assert set(attempted_downloads) == set(expected_downloads)
```

**Custom Generators**:

```python
# Strategy for generating Meeting objects
@st.composite
def meeting_strategy(draw):
    return Meeting(
        id=draw(st.uuids().map(str)),
        title=draw(st.text(min_size=1, max_size=100)),
        start_time=draw(st.datetimes()),
        end_time=draw(st.datetimes()),
        has_transcript=draw(st.booleans())
    )

# Strategy for valid date format strings
valid_date_formats = st.one_of(
    st.dates().map(lambda d: d.strftime('%Y-%m-%d')),
    st.dates().map(lambda d: d.strftime('%m/%d/%Y')),
    st.dates().map(lambda d: d.isoformat())
)

# Strategy for invalid date format strings
invalid_date_formats = st.text().filter(
    lambda s: not is_valid_date_format(s)
)
```

### Unit Testing

**Framework**: `pytest`

**Focus Areas**:

1. **Specific Examples**: Test concrete scenarios from requirements
2. **Edge Cases**: Empty inputs, boundary conditions, special characters
3. **Integration Points**: API mocking, file system interactions
4. **Error Conditions**: Specific error scenarios

**Unit Test Examples**:

```python
def test_prompt_credentials_displays_username_prompt(capsys):
    """Test that username prompt is displayed at startup."""
    # Feature: webex-transcript-downloader, Requirement 2.1
    with mock.patch('builtins.input', return_value='user@example.com'):
        with mock.patch('getpass.getpass', return_value='password'):
            username, password = prompt_credentials()

    captured = capsys.readouterr()
    assert 'username' in captured.out.lower()

def test_password_input_is_masked():
    """Test that password input uses getpass for masking."""
    # Feature: webex-transcript-downloader, Requirement 2.3
    with mock.patch('builtins.input', return_value='user@example.com'):
        with mock.patch('getpass.getpass', return_value='secret') as mock_getpass:
            username, password = prompt_credentials()

    mock_getpass.assert_called_once()
    assert password == 'secret'

def test_authentication_failure_displays_error_and_exits():
    """Test that authentication failures are handled gracefully."""
    # Feature: webex-transcript-downloader, Requirement 2.5
    with pytest.raises(SystemExit):
        with mock.patch('requests.post', side_effect=requests.HTTPError("401 Unauthorized")):
            authenticate('invalid@example.com', 'wrongpassword')

def test_empty_meeting_list_displays_zero_count():
    """Test handling of week with no meetings."""
    # Edge case for Requirement 4.5
    meetings = []
    summary = process_meetings(meetings)
    assert summary.total_meetings == 0
    assert summary.transcripts_downloaded == 0

def test_filename_with_special_characters():
    """Test sanitization of problematic filenames."""
    # Edge case for Requirement 5.3
    title = 'Q&A: What/How/Why? <Important>'
    date = datetime(2024, 1, 15)
    filename = sanitize_filename(title, date)

    assert filename == '2024-01-15_Q&A_What_How_Why_Important.txt'
    assert '<' not in filename
    assert '?' not in filename

def test_continue_after_download_failure():
    """Test that processing continues after individual failures."""
    # Feature: webex-transcript-downloader, Requirement 5.4
    meetings = [
        Meeting(id='1', title='Meeting 1', has_transcript=True),
        Meeting(id='2', title='Meeting 2', has_transcript=True),
        Meeting(id='3', title='Meeting 3', has_transcript=True),
    ]

    def mock_download(meeting_id):
        if meeting_id == '2':
            raise TranscriptError("Download failed")
        return "transcript content"

    results = process_meetings(meetings, download_func=mock_download)

    assert len(results) == 3
    assert results[0].success == True
    assert results[1].success == False
    assert results[2].success == True
```

### Test Organization

```
tests/
├── unit/
│   ├── test_input.py           # Input validation and prompts
│   ├── test_authentication.py  # Authentication logic
│   ├── test_api_client.py      # API interactions (mocked)
│   ├── test_file_handler.py    # File operations
│   └── test_main.py            # Main orchestration
├── property/
│   ├── test_properties.py      # All property-based tests
│   └── generators.py           # Custom hypothesis strategies
└── integration/
    └── test_end_to_end.py      # Full workflow with mocked API
```

### Test Coverage Goals

- **Line Coverage**: Minimum 90%
- **Branch Coverage**: Minimum 85%
- **Property Tests**: All 13 correctness properties implemented
- **Unit Tests**: All acceptance criteria with "example" or "edge-case" classification

### Continuous Integration

- Run all tests on every commit
- Run property tests with 100 iterations in CI
- Run property tests with 1000 iterations nightly
- Fail build if coverage drops below thresholds

### Manual Testing Checklist

Since this is a CLI script with user interaction, manual testing is also important:

- [ ] Test on Windows 10/11
- [ ] Test on macOS (latest version)
- [ ] Test with valid Webex credentials
- [ ] Test with invalid credentials
- [ ] Test with various date formats
- [ ] Test with week containing no meetings
- [ ] Test with week containing meetings without transcripts
- [ ] Test with network interruption during download
- [ ] Test with insufficient disk space
- [ ] Test with read-only output directory
