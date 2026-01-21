#!/bin/bash
# Simple launcher script for URL2MP3

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg is not installed or not in PATH"
    echo "Please install FFmpeg for audio conversion to work"
fi

# Check if dependencies are installed
if ! python3 -c "import yt_dlp" 2>/dev/null; then
    echo "Installing required dependencies..."
    pip3 install -r requirements.txt
fi

# Launch the application
python3 url2mp3.py
