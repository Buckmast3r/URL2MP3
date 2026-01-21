@echo off
REM Simple launcher script for URL2MP3 on Windows

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo Warning: FFmpeg is not installed or not in PATH
    echo Please install FFmpeg for audio conversion to work
)

REM Check if dependencies are installed
python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install -r requirements.txt
)

REM Launch the application
python url2mp3.py
pause
