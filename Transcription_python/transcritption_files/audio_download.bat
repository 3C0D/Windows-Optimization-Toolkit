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

:: Upgrade pip and install/update dependencies
@REM pip install --upgrade pip setuptools wheel
@REM pip install -r "%~dp0requirements.txt"

:: Run the Python script
python "%~dp0download_audio.py"


:: Pause to view results
pause

:: Deactivate the virtual environment
deactivate

:: Pause to view results
pause