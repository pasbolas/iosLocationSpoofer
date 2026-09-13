@echo off
title Install Apple Mobile Device Service
echo ============================================================
echo   Installing Apple Mobile Device Support (usbmuxd)...
echo ============================================================
echo.
echo Launching Apple Mobile Device Support Installer...
echo Please click 'Next' / 'Install' and allow the Windows prompt if asked.
echo.
msiexec.exe /i "%~dp0apple_extracted\AppleMobileDeviceSupport64.msi"
echo.
echo ============================================================
echo   Done!
echo   1. Unplug and replug your iPhone via USB.
echo   2. Unlock your iPhone screen and tap 'Trust' (enter passcode).
echo   3. In your browser at http://127.0.0.1:8000, click 'Scan USB'.
echo ============================================================
echo.
pause
