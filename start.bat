@echo off
chcp 65001 >nul 2>&1
title System Monitor

echo.
echo  ========================================
echo        System Monitor v1.0
echo  ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo [2/3] Checking dependencies...
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt -q
)

echo [3/3] Starting...
echo.
python main.py
