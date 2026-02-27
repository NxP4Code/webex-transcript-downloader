# Requirements Document

## Introduction

This document specifies requirements for a simple, interactive command-line script that fetches meeting transcripts from completed Webex meetings by week using the Webex API. The script prompts the user for credentials and week selection, then downloads available transcripts from meetings that have already ended. This MVP version does not support ongoing or in-progress meetings. The script must work on both Windows and Mac operating systems.

## Glossary

- **Script**: The interactive command-line application that fetches Webex transcripts
- **Webex_API**: The Webex REST API service for accessing meeting data
- **Transcript**: The text record of a Webex meeting's spoken content
- **Week_Range**: A time period defined by a start date and spanning 7 consecutive days
- **Meeting**: A completed Webex meeting session that may have an associated transcript

## Requirements

### Requirement 1: Cross-Platform Compatibility

**User Story:** As a user, I want the script to work on both Windows and Mac, so that I can use it regardless of my operating system.

#### Acceptance Criteria

1. THE Script SHALL execute successfully on Windows operating systems
2. THE Script SHALL execute successfully on macOS operating systems
3. THE Script SHALL use cross-platform file path handling for all file operations
4. THE Script SHALL use cross-platform libraries for all system interactions

### Requirement 2: Interactive Credential Input

**User Story:** As a user, I want to be prompted for my Webex credentials when I run the script, so that I can authenticate without using command-line parameters.

#### Acceptance Criteria

1. WHEN the Script starts, THE Script SHALL prompt the user to enter their Webex username
2. WHEN the username is entered, THE Script SHALL prompt the user to enter their Webex password
3. THE Script SHALL mask password input to prevent it from being displayed on screen
4. WHEN credentials are provided, THE Script SHALL authenticate with the Webex_API
5. IF authentication fails, THEN THE Script SHALL display a descriptive error message and exit

### Requirement 3: Interactive Week Selection

**User Story:** As a user, I want to be prompted for which week's transcripts to download, so that I can easily specify the time period.

#### Acceptance Criteria

1. WHEN authentication succeeds, THE Script SHALL prompt the user to enter a week start date
2. THE Script SHALL display the expected date format in the prompt
3. THE Script SHALL calculate the Week_Range as 7 consecutive days starting from the provided date
4. IF the date format is invalid, THEN THE Script SHALL display an error message and prompt again
5. THE Script SHALL validate that the provided date is in a recognized date format

### Requirement 4: Fetch Completed Meetings by Week

**User Story:** As a user, I want to retrieve all completed meetings within the specified week, so that I can identify which meetings have transcripts available.

#### Acceptance Criteria

1. WHEN a Week_Range is specified, THE Script SHALL query the Webex_API for all completed meetings within that range
2. THE Script SHALL retrieve meeting metadata including meeting ID, title, and transcript availability
3. THE Script SHALL exclude ongoing or in-progress meetings from the results
4. IF the API request fails, THEN THE Script SHALL display an error message and exit
5. THE Script SHALL display the count of completed meetings found within the Week_Range

### Requirement 5: Download Transcripts from Completed Meetings

**User Story:** As a user, I want to download transcripts from completed meetings that have them available, so that I can review meeting content offline.

#### Acceptance Criteria

1. FOR EACH completed Meeting with an available transcript, THE Script SHALL download the Transcript from the Webex_API
2. THE Script SHALL save each Transcript to a local file with a filename containing the meeting date and title
3. THE Script SHALL sanitize filenames to remove invalid filesystem characters on both Windows and Mac
4. IF a transcript download fails, THEN THE Script SHALL display an error message and continue with the next meeting
5. WHEN all transcripts are downloaded, THE Script SHALL display a summary of successful and failed downloads

### Requirement 6: Handle Missing Transcripts

**User Story:** As a user, I want to know which meetings don't have transcripts available, so that I can understand what data is missing.

#### Acceptance Criteria

1. WHEN a Meeting has no available transcript, THE Script SHALL display the meeting title and date
2. THE Script SHALL continue processing remaining meetings without interruption
3. THE Script SHALL include the count of meetings without transcripts in the final summary

### Requirement 7: Provide Progress Feedback

**User Story:** As a user, I want to see progress updates while the script runs, so that I know the script is working.

#### Acceptance Criteria

1. WHILE downloading transcripts, THE Script SHALL display progress information including current meeting number and total count
2. WHEN downloading a transcript, THE Script SHALL display the meeting title being processed
3. WHEN a transcript download completes, THE Script SHALL display a success message
4. WHEN all downloads complete, THE Script SHALL display a summary including total completed meetings found, transcripts downloaded, and any errors encountered
