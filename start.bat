@echo off
chcp 65001 >nul 2>&1
title System Monitor v2.2

echo.
echo  ========================================
echo    System Monitor v2.2
echo    系统监控工具 v2.2
echo  ========================================
echo.
cd /d "%~dp0"

echo [1/3] 正在检查 Python... / Checking Python...
python --version 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python！ / Python not found!
    pause
    exit /b 1
)

echo [2/3] 正在检查依赖包... / Checking dependencies...
python -c "import psutil" 2>nul
if errorlevel 1 (
    echo 正在安装依赖包... / Installing dependencies...
    pip install -r requirements.txt -q
)

echo [3/3] 正在启动... / Starting...
echo.
echo  请稍候，正在加载系统信息...
echo  Please wait, loading system info...
echo.
python main.py
