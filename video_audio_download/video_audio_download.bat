@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ================================================
echo  Video/Audio Downloader - UV Edition
echo ================================================
echo.

REM Check if UV is installed
where uv >nul 2>&1
if errorlevel 1 (
    echo [ERROR] UV is not installed!
    echo.
    echo To install UV, run in PowerShell:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    echo Or visit: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Sync dependencies (creates venv if needed, installs/updates packages)
echo Installing/updating dependencies...
uv sync

REM Run the script with UV
echo.
echo Starting the downloader...
echo ================================================
echo.
uv run python download_video_audio.py

echo.
echo ================================================
pause
