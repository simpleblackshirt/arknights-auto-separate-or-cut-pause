@echo off
REM Arknights Auto Separate/Cut Pause Tool - Windows Setup Script
REM This script creates a virtual environment and downloads FFmpeg binaries

echo ========================================
echo Arknights Cut Tool - Windows Setup
echo ========================================
echo.

REM Check Python 3.12 is installed
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 is required but not found
    echo Please install Python 3.12 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Using Python 3.12...
for /f "tokens=2" %%i in ('py -3.12 --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
py -3.12 -m venv venv
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
py -3.12 -m pip install --upgrade pip
echo.

echo Installing Python dependencies...
py -3.12 -m pip install -r requirements.txt
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
echo Downloading FFmpeg binaries (this may take a moment, ~100MB)...
echo.

REM Download and extract FFmpeg from BtbN builds
echo Downloading FFmpeg zip...
curl -L -o ffmpeg.zip https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
if errorlevel 1 (
    echo ERROR: Failed to download FFmpeg
    echo Please download manually from: https://github.com/BtbN/FFmpeg-Builds/releases/latest
    pause
    exit /b 1
)

echo Extracting FFmpeg binaries...
powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath ffmpeg_temp -Force"
move ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe bin\
move ffmpeg_temp\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe bin\
rmdir /s /q ffmpeg_temp
del ffmpeg.zip

echo FFmpeg binaries downloaded and extracted successfully.

:skip_ffmpeg_download

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the application: py -3.12 cut_tool.py
echo   OR: python cut_tool.py (when venv is active)
echo.
echo.
pause
