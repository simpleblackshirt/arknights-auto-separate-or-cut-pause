@echo off
REM Arknights Auto Separate/Cut Pause Tool - Windows Setup Script
REM This script creates a virtual environment and downloads FFmpeg binaries

echo ========================================
echo Arknights Cut Tool - Windows Setup
echo ========================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is required but not found
    echo Please install Python 3.12 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

REM Activate virtual environment and install dependencies
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Create bin directory
echo Creating bin directory for FFmpeg...
if not exist bin mkdir bin

REM Check if FFmpeg binaries already exist
set FFMPEG_MISSING=0
if not exist bin\ffmpeg.exe set FFMPEG_MISSING=1
if not exist bin\ffprobe.exe set FFMPEG_MISSING=1

if %FFMPEG_MISSING%==0 (
    echo FFmpeg binaries already exist in bin\ folder. Skipping download.
    echo.
    goto :skip_ffmpeg_download
)

REM Download FFmpeg binaries
echo.
echo Downloading FFmpeg binaries (this may take a moment, files are ~110MB total)...
echo.

REM Download ffmpeg.exe
if not exist bin\ffmpeg.exe (
    echo Downloading ffmpeg.exe...
    curl -L -o bin\ffmpeg.exe https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip-bin/ffmpeg.exe
    if errorlevel 1 (
        echo WARNING: Failed to download ffmpeg.exe from primary URL
        echo Trying alternative source...
        curl -L -o bin\ffmpeg.exe https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
        if errorlevel 1 (
            echo ERROR: Failed to download FFmpeg
            echo Please download manually from: https://www.gyan.dev/ffmpeg/builds/
            echo Extract ffmpeg.exe and ffprobe.exe to the bin\ directory
            pause
            exit /b 1
        )
    )
) else (
    echo ffmpeg.exe already exists, skipping download.
)

REM Download ffprobe.exe
if not exist bin\ffprobe.exe (
    echo Downloading ffprobe.exe...
    curl -L -o bin\ffprobe.exe https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip-bin/ffprobe.exe
    if errorlevel 1 (
        echo WARNING: Failed to download ffprobe.exe from primary URL
        echo Trying alternative source...
        curl -L -o bin\ffprobe.exe https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
        if errorlevel 1 (
            echo ERROR: Failed to download FFprobe
            echo Please download manually from: https://www.gyan.dev/ffmpeg/builds/
            echo Extract ffmpeg.exe and ffprobe.exe to the bin\ directory
            pause
            exit /b 1
        )
    )
) else (
    echo ffprobe.exe already exists, skipping download.
)

:skip_ffmpeg_download

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the application: python cut_tool.py
echo.
echo.
pause
