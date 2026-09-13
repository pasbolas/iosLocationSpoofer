@echo off
title iOS Developer Mode Enabler
echo ============================================================
echo   Revealing iOS Developer Mode on iPhone...
echo ============================================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv.
    pause
    exit /b 1
)

.venv\Scripts\python.exe reveal_dev_mode.py

echo.
pause
