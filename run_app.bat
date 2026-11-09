@echo off
title CSAB Choice Filling Assistant
echo =======================================================
echo   Starting CSAB Choice Filling Assistant...
echo   Opening in your browser at: http://localhost:8000
echo =======================================================
cd /d "%~dp0"

start http://localhost:8000

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" app.py
) else (
    python app.py
)
pause
