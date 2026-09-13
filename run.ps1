Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting iPhone Location Simulator..." -ForegroundColor Green
Write-Host "  Local URL: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found." -ForegroundColor Red
    Write-Host "Run: python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Open browser
Start-Process "http://127.0.0.1:8000"

# Run FastAPI server
& ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
