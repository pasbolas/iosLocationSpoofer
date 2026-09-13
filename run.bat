@echo off
title iPhone Location Simulator
echo ============================================================
echo   Starting iPhone Location Simulator...
echo   Local Address: http://127.0.0.1:8000
echo ============================================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Please run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Launch default browser in background after 1 second
start "" cmd /c "timeout /t 1 /nobreak >nul && start http://127.0.0.1:8000"

:: Start FastAPI backend
call .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause
