@echo off
chcp 65001 >nul 2>&1
title System Monitor v2.0

echo.
echo  ========================================
echo    System Monitor v2.0
echo  ========================================
echo.
cd /d "%~dp0"

echo [1/3] 正在检查 Python...
python --version 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！
    pause
    exit /b 1
)

echo [2/3] 正在检查依赖包...
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt -q
)

echo [3/3] 正在启动...
echo.
python main.py
