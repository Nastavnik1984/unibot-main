@echo off
chcp 65001 >nul
title Создание виртуального окружения с Python 3.11
color 0A
echo ========================================
echo   СОЗДАНИЕ ВИРТУАЛЬНОГО ОКРУЖЕНИЯ
echo   С PYTHON 3.11
echo ========================================
echo.

REM Переходим в директорию скрипта
cd /d "%~dp0"

echo Проверка Python 3.11...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.11 не найден!
    echo.
    echo Установите Python 3.11:
    echo   1. Запустите setup_python311.bat
    echo   2. Или скачайте с https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

py -3.11 --version
echo ✅ Python 3.11 найден
echo.

echo Удаление старого виртуального окружения (если есть)...
if exist .venv (
    rmdir /s /q .venv
    echo ✅ Старое окружение удалено
)
echo.

echo Создание нового виртуального окружения с Python 3.11...
py -3.11 -m venv .venv
if errorlevel 1 (
    echo ❌ Ошибка создания виртуального окружения!
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение создано
echo.

echo Активация окружения и обновление pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo ✅ pip обновлён
echo.

echo Установка зависимостей...
echo Это может занять несколько минут...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей!
    pause
    exit /b 1
)

pip install -r requirements-dev.txt
if errorlevel 1 (
    echo ❌ Ошибка установки dev зависимостей!
    pause
    exit /b 1
)
echo ✅ Все зависимости установлены
echo.

echo ========================================
echo   ✅ ГОТОВО!
echo ========================================
echo.
echo Виртуальное окружение создано с Python 3.11
echo.
echo Для активации окружения:
echo   .venv\Scripts\activate.bat
echo.
echo Для запуска бота:
echo   uvicorn src.main:app --reload
echo.
pause




