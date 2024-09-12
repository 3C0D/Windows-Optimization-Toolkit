@echo off
setlocal enabledelayedexpansion

REM Chemin vers le fichier node.exe (modifiez ce chemin si nécessaire)
set "nodePath=C:\Program Files\nodejs\node.exe"

REM Chemin vers le script generateFileContent.js (modifiez ce chemin si nécessaire)
set "generateScript=%~dp0generateFileContent.js"

REM Chemin du fichier à lire
set "file=%~1"
set "file=!file:\=/!"
set "file=!file: =%%20!"

REM Exécuter le script Node.js pour générer fileContent.js
"%nodePath%" "%generateScript%" "!file!"

REM Attendre quelques secondes pour s'assurer que le fichier JS est généré
timeout /t 2 /nobreak > nul

REM Ouvrir le fichier HTML dans le navigateur
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "%~dp0liseuse.html"

endlocal
