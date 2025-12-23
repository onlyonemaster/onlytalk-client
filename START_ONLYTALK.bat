@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo   OnlyTalk 클라이언트 시작
echo ========================================
echo.
python client_main.py
pause
