@echo off
set scriptDir=%~dp0
PowerShell -NoProfile -ExecutionPolicy Bypass -File "%scriptDir%wifi.ps1"
@REM pause
@REM Attendre 2,5 secondes avant de fermer la fenêtre
PowerShell -Command "Start-Sleep -Milliseconds 2200"
