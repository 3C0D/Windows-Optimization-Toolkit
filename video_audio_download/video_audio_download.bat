@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Define the path to the virtual environment
set VENV_PATH=%~dp0venv

:: Check if the virtual environment exists, create it if not
if not exist "%VENV_PATH%" (
    echo Création de l'environnement virtuel et installation des bibliothèques...
    echo Cette opération prendra environ 30 secondes, veuillez patienter...
    python -m venv "%VENV_PATH%"
)

:: Activate the virtual environment
call "%VENV_PATH%\Scripts\activate"

:: Les mises à jour de yt-dlp et l'exportation des cookies sont maintenant gérées par le script Python

:: Run the Python script
python "%~dp0download_video_audio.py"

:: Pause to view results
pause

:: Deactivate the virtual environment
deactivate
