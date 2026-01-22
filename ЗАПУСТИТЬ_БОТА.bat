@echo off
chcp 65001 >nul
title Unibot - Telegram Bot
color 0A

cd /d "%~dp0"

echo ========================================
echo   ЗАПУСК UNIBOT
echo ========================================
echo.
echo Запуск бота с hot reload...
echo.
echo Для остановки нажмите Ctrl+C
echo.
echo Проверка работы:
echo   - Админка: http://localhost:8000/admin
echo   - Health:  http://localhost:8000/health
echo.

.venv\Scripts\uvicorn.exe src.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000

pause




