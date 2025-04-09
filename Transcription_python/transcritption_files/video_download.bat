@echo off
setlocal enabledelayedexpansion

:: Define the path to the virtual environment
set VENV_PATH=%~dp0venv

:: Check if the virtual environment exists, create it if not
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
)

:: Activate the virtual environment
call "%VENV_PATH%\Scripts\activate"

:: Check if yt-dlp needs updating (only updates if needed)
echo Checking for yt-dlp updates...
yt-dlp --update-to stable

:: Check if cookies file exists, if not, try to export it
if not exist "%~dp0cookies.txt" (
    echo Trying to export cookies from Chrome...
    python "%~dp0export_cookies.py"
)

:: Run the Python script
python "%~dp0download_video.py"

:: Pause to view results
pause

:: Deactivate the virtual environment
deactivate
