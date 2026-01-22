@echo off
chcp 65001 >nul
title Проверка проекта Unibot
color 0E
echo ========================================
echo   ПРОВЕРКА ПРОЕКТА UNIBOT
echo ========================================
echo.

REM Переходим в директорию скрипта
cd /d "%~dp0"

echo [1/7] Проверка Python 3.11...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден в PATH!
    echo.
    echo Установите Python 3.11 с официального сайта:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version | findstr /C:"3.11" >nul
if errorlevel 1 (
    echo ⚠️  Найден Python, но не версия 3.11
    python --version
    pause
    exit /b 1
)

python --version
echo ✅ Python 3.11 найден
echo.

echo [2/7] Проверка виртуального окружения...
if not exist .venv (
    echo ❌ Виртуальное окружение не найдено!
    echo Запустите setup_project.bat для установки
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение существует
echo.

echo [3/7] Активация виртуального окружения...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Ошибка активации виртуального окружения!
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение активировано
echo.

echo [4/7] Проверка установленных зависимостей...
python -c "import aiogram; import fastapi; import sqlalchemy; import alembic; print('✅ Основные зависимости установлены')" 2>nul
if errorlevel 1 (
    echo ❌ Зависимости не установлены!
    echo Запустите: pip install -r requirements.txt -r requirements-dev.txt
    pause
    exit /b 1
)
echo.

echo [5/7] Проверка файла .env...
if not exist .env (
    echo ⚠️  Файл .env не найден
    if exist .env.example (
        echo Создаю .env из .env.example...
        copy .env.example .env >nul
        echo ✅ Файл .env создан
        echo ⚠️  ВАЖНО: Откройте .env и укажите BOT__TOKEN!
    ) else (
        echo ❌ Файл .env.example не найден!
    )
) else (
    echo ✅ Файл .env существует
)
echo.

echo [6/7] Проверка синтаксиса Python кода...
python -m py_compile src\main.py 2>nul
if errorlevel 1 (
    echo ⚠️  Ошибка компиляции src\main.py
) else (
    echo ✅ Синтаксис кода корректен
)
echo.

echo [7/7] Проверка миграций...
if exist alembic\versions (
    echo ✅ Папка миграций существует
    dir /b alembic\versions\*.py 2>nul | find /c ".py" >nul
    if errorlevel 1 (
        echo ⚠️  Файлы миграций не найдены
    ) else (
        echo ✅ Файлы миграций найдены
    )
) else (
    echo ⚠️  Папка миграций не найдена
)
echo.

echo ========================================
echo   ИТОГИ ПРОВЕРКИ
echo ========================================
echo.
echo Для полной установки запустите: setup_project.bat
echo.
echo Для запуска бота:
echo   1. Активируйте окружение: .venv\Scripts\activate.bat
echo   2. Запустите: uvicorn src.main:app --reload
echo.
pause




