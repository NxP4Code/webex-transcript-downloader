# Implementation Plan: Webex Transcript Downloader

## Overview

This implementation plan breaks down the Webex Transcript Downloader into incremental coding tasks. The script is a single-file Python CLI application that authenticates with Webex, prompts for a week range, fetches completed meetings, and downloads available transcripts. Each task builds on previous work, with property-based tests using hypothesis to validate correctness properties.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Setup virtual envirnoment for python.
  - Create main script file `webex_transcript_downloader.py`
  - Create `requirements.txt` with dependencies: requests, hypothesis (for testing)
  - Create `tests/` directory structure with `unit/`, `property/`, and `integration/` subdirectories
  - _Requirements: 1.4_

- [x] 2. Implement data models and type definitions
  - [x] 2.1 Create Meeting dataclass with id, title, start_time, end_time, has_transcript fields
    - Use Python dataclasses for clean structure
    - Include type hints for all fields
    - _Requirements: 4.2_
  - [x] 2.2 Create DownloadResult dataclass for tracking download outcomes
    - Include meeting reference, success flag, optional error message and filename
    - _Requirements: 5.5_
  - [x] 2.3 Create Summary dataclass for final statistics
    - Include counts for total meetings, downloaded, unavailable, and failed
    - Include list of failed meetings with error messages
    - _Requirements: 6.3, 7.4_
  - [ ]\* 2.4 Write property test for meeting metadata completeness
    - **Property 7: Meeting Metadata Completeness**
    - **Validates: Requirements 4.2**

- [x] 3. Implement input module for user prompts
  - [x] 3.1 Implement prompt_credentials() function
    - Use input() for username prompt
    - Use getpass.getpass() for masked password input
    - Return tuple of (username, password)
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 3.2 Implement prompt_week_start_date() function with validation
    - Display expected date format in prompt
    - Parse multiple date formats (YYYY-MM-DD, MM/DD/YYYY, ISO 8601)
    - Retry up to 3 times on invalid input
    - Raise ValueError after max retries
    - _Requirements: 3.1, 3.2, 3.4, 3.5_
  - [x] 3.3 Implement calculate_week_range() function
    - Take start date and return end date exactly 7 days later
    - Use timedelta for date arithmetic
    - _Requirements: 3.3_
  - [ ]\* 3.4 Write property test for week range calculation
    - **Property 1: Week Range Calculation**
    - **Validates: Requirements 3.3**
  - [ ]\* 3.5 Write property test for date format validation
    - **Property 2: Date Format Validation**
    - **Validates: Requirements 3.4, 3.5**

- [x] 4. Checkpoint - Verify input module functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement authentication module
  - [x] 5.1 Create custom AuthenticationError exception class
    - Inherit from Exception with descriptive message
    - _Requirements: 2.5_
  - [x] 5.2 Implement authenticate() function
    - Accept username and password parameters
    - Make POST request to Webex authentication endpoint
    - Return access token on success
    - Raise AuthenticationError with descriptive message on failure
    - _Requirements: 2.4, 2.5_
  - [ ]\* 5.3 Write property test for authentication error handling
    - **Property 5: Authentication Error Handling**
    - **Validates: Requirements 2.5**
  - [ ]\* 5.4 Write unit tests for authentication module
    - Test successful authentication with valid credentials
    - Test authentication failure with invalid credentials
    - Test network error handling
    - _Requirements: 2.4, 2.5_

- [x] 6. Implement API client module for Webex interactions
  - [x] 6.1 Create custom APIError and TranscriptNotAvailableError exception classes
    - Define clear error messages for each scenario
    - _Requirements: 4.4, 5.4_
  - [x] 6.2 Implement fetch_meetings() function
    - Accept token, start_date, and end_date parameters
    - Make GET request to Webex meetings endpoint with date range and state=ended
    - Parse response and create Meeting objects
    - Filter to only include completed meetings
    - Raise APIError on request failures
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 6.3 Implement download_transcript() function
    - Accept token and meeting_id parameters
    - Make GET request to Webex transcript endpoint
    - Return transcript text content
    - Raise TranscriptNotAvailableError if transcript not found
    - Raise APIError on other failures
    - _Requirements: 5.1_
  - [ ]\* 6.4 Write property test for meeting filtering
    - **Property 6: Meeting Filtering**
    - **Validates: Requirements 4.3**
  - [ ]\* 6.5 Write property test for API query parameters
    - **Property 8: API Query Parameters**
    - **Validates: Requirements 4.1**
  - [ ]\* 6.6 Write property test for download attempt coverage
    - **Property 9: Download Attempt Coverage**
    - **Validates: Requirements 5.1**
  - [ ]\* 6.7 Write unit tests for API client module
    - Test fetch_meetings with mocked API responses
    - Test download_transcript with mocked responses
    - Test error handling for various API failures
    - _Requirements: 4.1, 4.4, 5.1_

- [x] 7. Checkpoint - Verify API client functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement file handler module
  - [x] 8.1 Implement sanitize_filename() function
    - Accept meeting title and date parameters
    - Remove/replace invalid characters: < > : " / \ | ? \*
    - Format as YYYY-MM-DD_sanitized_title.txt
    - Limit filename length to 255 characters
    - _Requirements: 5.2, 5.3_
  - [x] 8.2 Implement save_transcript() function
    - Accept content, filename, and output_dir parameters
    - Use pathlib.Path for cross-platform path handling
    - Create output directory if it doesn't exist
    - Write transcript content to file
    - Raise IOError on write failures
    - _Requirements: 1.3, 5.2_
  - [ ]\* 8.3 Write property test for filename sanitization
    - **Property 3: Filename Sanitization**
    - **Validates: Requirements 5.2, 5.3**
  - [ ]\* 8.4 Write property test for cross-platform path handling
    - **Property 4: Cross-Platform Path Handling**
    - **Validates: Requirements 1.3**
  - [ ]\* 8.5 Write unit tests for file handler module
    - Test sanitization with various special characters
    - Test file saving with mocked filesystem
    - Test error handling for I/O failures
    - _Requirements: 5.2, 5.3_

- [x] 9. Implement main orchestrator and workflow coordination
  - [x] 9.1 Implement process_meetings() function
    - Accept list of meetings and download function
    - Iterate through meetings with has_transcript=True
    - Attempt download for each meeting
    - Continue processing on individual failures
    - Return list of DownloadResult objects
    - _Requirements: 5.1, 5.4, 6.2_
  - [x] 9.2 Implement display_progress() function
    - Show current meeting number and total count
    - Display meeting title being processed
    - _Requirements: 7.1, 7.2_
  - [x] 9.3 Implement display_summary() function
    - Show total meetings found
    - Show transcripts downloaded count
    - Show transcripts unavailable count
    - Show failed downloads with error messages
    - _Requirements: 5.5, 6.3, 7.4_
  - [x] 9.4 Implement main() function to orchestrate complete workflow
    - Call prompt_credentials() and authenticate()
    - Call prompt_week_start_date() and calculate_week_range()
    - Call fetch_meetings() and display count
    - Call process_meetings() with progress display
    - Call display_summary() with results
    - Handle critical errors (authentication, API failures) by displaying message and exiting
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 4.1, 4.4, 4.5, 5.4, 5.5, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4_
  - [ ]\* 9.5 Write property test for error resilience
    - **Property 10: Error Resilience**
    - **Validates: Requirements 5.4, 6.2**
  - [ ]\* 9.6 Write property test for summary statistics accuracy
    - **Property 11: Summary Statistics Accuracy**
    - **Validates: Requirements 5.5, 6.3, 7.4**
  - [ ]\* 9.7 Write property test for progress information completeness
    - **Property 12: Progress Information Completeness**
    - **Validates: Requirements 7.1, 7.2, 7.3**
  - [ ]\* 9.8 Write property test for meeting count accuracy
    - **Property 13: Meeting Count Accuracy**
    - **Validates: Requirements 4.5**

- [x] 10. Add script entry point and logging configuration
  - [x] 10.1 Add if **name** == "**main**" block to call main()
    - Wrap in try-except to catch and display any unhandled errors
    - Exit with appropriate status codes
    - _Requirements: 1.1, 1.2_
  - [x] 10.2 Configure logging to file
    - Set up logging to webex_transcript_downloader.log
    - Log all API requests and responses (excluding sensitive data)
    - Log all errors with stack traces
    - Keep console output user-friendly
    - _Requirements: 2.5, 4.4, 5.4_

- [x] 11. Checkpoint - Verify complete workflow
  - Ensure all tests pass, ask the user if questions arise.

- [ ]\* 12. Create hypothesis custom generators for property tests
  - [ ]\* 12.1 Create meeting_strategy() composite generator
    - Generate Meeting objects with random but valid data
    - Use hypothesis strategies for each field type
    - _Requirements: 4.2_
  - [ ]\* 12.2 Create date format strategies
    - Create valid_date_formats strategy for valid date strings
    - Create invalid_date_formats strategy for invalid date strings
    - _Requirements: 3.4, 3.5_
  - [ ]\* 12.3 Configure hypothesis settings
    - Set minimum 100 iterations per test
    - Create CI profile for automated testing
    - _Requirements: All_

- [ ]\* 13. Create integration tests
  - [ ]\* 13.1 Write end-to-end test with fully mocked API
    - Mock all API endpoints
    - Test complete workflow from credentials to summary
    - Verify file creation and content
    - _Requirements: All_

- [x] 14. Final checkpoint - Complete testing and validation
  - Run all unit tests and property tests
  - Verify cross-platform compatibility (Windows and Mac)
  - Ensure all requirements are covered
  - Ask the user if any questions or issues arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- For this project use local venv, dont install and run global python commands
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- The script is implemented as a single file for simplicity
- All file operations use pathlib for cross-platform compatibility
- Authentication and API interactions use the requests library
- Password input uses getpass for security
