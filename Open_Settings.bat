@echo off
title HandWave Settings
cd /d "%~dp0"

if exist "HandWave.exe" (
    start "" "HandWave.exe" --settings
) else (
    python settings_gui.py
)
