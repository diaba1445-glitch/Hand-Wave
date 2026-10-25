@echo off
title HandWave - Setup Dependencies
cd /d "%~dp0"
echo ========================================================
echo       HandWave - Installing Required Dependencies
echo ========================================================
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install packages.
    echo Please make sure Python 3.10+ is installed and added to PATH.
    echo.
    pause
    exit /b 1
)
echo.
echo [SUCCESS] Dependencies installed successfully!
echo You can now launch HandWave using Start_HandWave.bat
echo.
pause
