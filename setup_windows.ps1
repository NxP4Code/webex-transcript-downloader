# ============================================
# Webex Transcript Downloader - Windows Setup
# ============================================

Write-Host "========================================"
Write-Host "Webex Transcript Downloader - Windows Setup"
Write-Host "========================================"
Write-Host ""

# Check if Python is installed
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3") {
            $pythonCmd = $cmd
            Write-Host "Found $version"
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "Python 3 is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Python:"
    Write-Host "  1. Go to https://www.python.org/downloads/"
    Write-Host "  2. Download the latest Python 3 installer"
    Write-Host "  3. Run the installer"
    Write-Host "  4. IMPORTANT: Check 'Add Python to PATH' during installation"
    Write-Host "  5. Close and reopen PowerShell"
    Write-Host "  6. Run this script again"
    Write-Host ""
    exit 1
}

# Check Python version is 3.8+
$versionCheck = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
$parts = $versionCheck.Split(".")
$major = [int]$parts[0]
$minor = [int]$parts[1]
if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
    Write-Host "Python 3.8 or higher is required. You have Python $versionCheck" -ForegroundColor Red
    Write-Host "Please update Python from https://www.python.org/downloads/"
    exit 1
}

Write-Host ""

# Create virtual environment
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Updating..."
} else {
    Write-Host "Creating virtual environment..."
    & $pythonCmd -m venv venv
}

# Activate and install dependencies
Write-Host "Installing dependencies..."
& .\venv\Scripts\Activate.ps1
& .\venv\Scripts\pip install --upgrade pip --quiet
& .\venv\Scripts\pip install -r requirements.txt --quiet

Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    "WEBEX_ACCESS_TOKEN=" | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Created .env file."
    Write-Host ""
    Write-Host "IMPORTANT: You need to add your Webex access token." -ForegroundColor Yellow
    Write-Host "  1. Go to https://developer.webex.com"
    Write-Host "  2. Sign in and copy your Personal Access Token"
    Write-Host "  3. Open the .env file and paste it after WEBEX_ACCESS_TOKEN="
} else {
    Write-Host ".env file already exists."
}

Write-Host ""
Write-Host "========================================"
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""
Write-Host "To run the tool:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host "  python webex_transcript_downloader.py"
Write-Host ""
