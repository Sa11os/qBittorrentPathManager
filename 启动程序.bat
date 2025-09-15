@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动NAS路径转换工具 喵~
echo.
.venv\Scripts\python.exe main.py
pause