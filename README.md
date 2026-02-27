# Webex Transcript Downloader

A simple tool that downloads meeting transcripts from your Webex meetings.

## What You Need

- A computer (Mac or Windows)
- Internet connection
- A Webex account with access to meeting transcripts

## Quick Setup

### Mac

1. Open **Terminal** (search for "Terminal" in Spotlight)
2. Navigate to this folder:
   ```
   cd path/to/webex-transcripts
   ```
3. Run the setup script:
   ```
   bash setup_mac.sh
   ```

### Windows

1. Open **PowerShell** (search for "PowerShell" in the Start menu)
2. Navigate to this folder:
   ```
   cd path\to\webex-transcripts
   ```
3. Run the setup script:
   ```
   powershell -ExecutionPolicy Bypass -File setup_windows.ps1
   ```

## Getting Your Webex Access Token

Before running the tool, you need a personal access token from Webex:

1. Go to https://developer.webex.com
2. Sign in with your Webex account
3. Click your avatar/profile icon in the top right
4. You'll see your **Personal Access Token** — copy it
5. Open the `.env` file in this folder and paste it:
   ```
   WEBEX_ACCESS_TOKEN=paste_your_token_here
   ```

> **Note:** This token expires after 12 hours. You'll need to get a new one each day you use the tool.

## Running the Tool

### Mac

```
source venv/bin/activate
python webex_transcript_downloader.py
```

### Windows

```
venv\Scripts\activate
python webex_transcript_downloader.py
```

The tool will:

1. Verify your access token
2. Ask you for a week start date (e.g., 2026-02-23)
3. Find all completed meetings in that week
4. Download any available transcripts to the `transcripts/` folder

## Where Are My Transcripts?

Downloaded transcripts are saved in the `transcripts/` folder, named like:

```
2026-02-26_Meeting Title.txt
```

## Troubleshooting

| Problem                       | Solution                                                                            |
| ----------------------------- | ----------------------------------------------------------------------------------- |
| "No WEBEX_ACCESS_TOKEN found" | Make sure you added your token to the `.env` file                                   |
| "Invalid access token"        | Your token expired — get a new one from developer.webex.com                         |
| "No meetings found"           | Try a different week — make sure you had meetings that week                         |
| "0 transcripts downloaded"    | Transcripts are only available for meetings you hosted with Webex Assistant enabled |
| Python not found after setup  | Close and reopen your Terminal/PowerShell, then try again                           |

## Known Limitations

- **Hosted meetings only:** The Webex API with a personal access token only returns transcripts for meetings you hosted (scheduled). Transcripts for meetings you attended but didn't host are not available through the API, even though they appear in the Webex UI. This is a Webex API limitation, not a bug in this tool.
- Only meetings with Webex Assistant or Closed Captions enabled will have transcripts
- The tool only downloads transcripts from meetings that have already ended
- Transcripts are saved as plain text (.txt) files
- Personal access tokens expire after 12 hours
