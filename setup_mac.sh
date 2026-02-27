#!/bin/bash
# ============================================
# Webex Transcript Downloader - Mac Setup
# ============================================

set -e

echo "========================================"
echo "Webex Transcript Downloader - Mac Setup"
echo "========================================"
echo ""

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "Found $PYTHON_VERSION"
else
    echo "Python 3 is not installed."
    echo ""
    echo "To install Python:"
    echo "  Option 1: Download from https://www.python.org/downloads/"
    echo "  Option 2: If you have Homebrew, run: brew install python3"
    echo ""
    echo "After installing Python, run this script again."
    exit 1
fi

# Check Python version is 3.8+
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Python 3.8 or higher is required. You have Python $PYTHON_MAJOR.$PYTHON_MINOR"
    echo "Please update Python from https://www.python.org/downloads/"
    exit 1
fi

echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Updating..."
else
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "WEBEX_ACCESS_TOKEN=" > .env
    echo "Created .env file."
    echo ""
    echo "IMPORTANT: You need to add your Webex access token."
    echo "  1. Go to https://developer.webex.com"
    echo "  2. Sign in and copy your Personal Access Token"
    echo "  3. Open the .env file and paste it after WEBEX_ACCESS_TOKEN="
else
    echo ".env file already exists."
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To run the tool:"
echo "  source venv/bin/activate"
echo "  python webex_transcript_downloader.py"
echo ""
