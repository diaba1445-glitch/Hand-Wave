@echo off
title HandWave
cd /d "%~dp0"

if exist "HandWave.exe" (
    start "" "HandWave.exe"
) else (
    python HandWave.py
    if errorlevel 1 pause
)
