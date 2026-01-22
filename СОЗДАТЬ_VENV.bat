@echo off
chcp 65001 >nul
title Создание виртуального окружения
color 0A
echo ========================================
echo   СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ
echo ========================================
echo.

cd /d "%~dp0"

echo Проверка Python...
python --version
if errorlevel 1 (
    echo ❌ Python не найден!
    pause
    exit /b 1
)

echo.
echo Удаление старого окружения (если есть)...
if exist .venv (
    rmdir /s /q .venv
    echo ✅ Удалено
)

echo.
echo Создание виртуального окружения...
python -m venv .venv
if errorlevel 1 (
    echo ❌ Ошибка!
    pause
    exit /b 1
)

echo ✅ Виртуальное окружение создано
echo.
echo Активируйте окружение:
echo   .venv\Scripts\activate.bat
echo.
echo Затем установите зависимости:
echo   pip install -r requirements.txt
echo   pip install -r requirements-dev.txt
echo.
pause




