@echo off
title HandWave
cd /d "%~dp0"
python HandWave.py
if errorlevel 1 pause
