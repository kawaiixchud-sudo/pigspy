#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing PigSpy dependencies..."
echo

# Install system dependencies
echo "Checking for system dependencies..."
if ! dpkg -l | grep -q libvlc-dev; then
    echo "Installing VLC libraries..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y libvlc-dev vlc-bin ffmpeg
    else
        echo "Warning: Could not detect apt-get. Please install libvlc-dev and ffmpeg manually."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo
        echo "Error creating virtual environment. Please ensure python3-venv is installed."
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies in virtual environment..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "Note: If pyaudio failed to install, you may need portaudio."
    echo "Try installing: sudo apt-get install portaudio19-dev"
    echo "Then run this script again."
    exit 1
fi

echo
echo "Dependencies installed successfully!"
echo
echo "Running PigSpy..."
echo
python3 main.py