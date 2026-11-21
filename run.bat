@echo off
title CropCare AI Server Launcher
cd /d "%~dp0"

echo ===================================================
echo   Starting CropCare AI (Flask Application Server)
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Automatically open browser after 2 seconds in the background
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:5000"

:: Start Flask app
python app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server terminated with an error.
    pause
)
