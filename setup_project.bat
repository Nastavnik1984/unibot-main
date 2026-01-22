@echo off
chcp 65001 >nul
title Настройка проекта Unibot
color 0B
echo ========================================
echo   НАСТРОЙКА ПРОЕКТА UNIBOT
echo ========================================
echo.

REM Переходим в директорию скрипта
cd /d "%~dp0"

echo [1/6] Проверка Python 3.11...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден в PATH!
    echo.
    echo Установите Python 3.11 с официального сайта:
    echo https://www.python.org/downloads/
    echo.
    echo ВАЖНО: При установке отметьте "Add Python to PATH"
    pause
    exit /b 1
)

python --version | findstr /C:"3.11" >nul
if errorlevel 1 (
    echo ⚠️  Найден Python, но не версия 3.11
    python --version
    echo.
    echo Установите Python 3.11 с официального сайта:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python 3.11 найден
echo.

echo [2/6] Создание виртуального окружения...
if exist .venv (
    echo ⚠️  Виртуальное окружение уже существует
    echo Удаляю старое окружение...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo ❌ Ошибка создания виртуального окружения!
    pause
    exit /b 1
)
echo ✅ Виртуальное окружение создано
echo.

echo [3/6] Активация виртуального окружения и обновление pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ Ошибка обновления pip!
    pause
    exit /b 1
)
echo ✅ pip обновлён
echo.

echo [4/6] Установка зависимостей...
echo Это может занять несколько минут...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей из requirements.txt!
    pause
    exit /b 1
)

pip install -r requirements-dev.txt
if errorlevel 1 (
    echo ❌ Ошибка установки зависимостей из requirements-dev.txt!
    pause
    exit /b 1
)
echo ✅ Все зависимости установлены
echo.

echo [5/6] Настройка файла .env...
if exist .env (
    echo ⚠️  Файл .env уже существует
    echo Пропускаю копирование .env.example
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ Файл .env создан из .env.example
        echo.
        echo ⚠️  ВАЖНО: Откройте файл .env и укажите:
        echo    - BOT__TOKEN=ваш_токен_бота
        echo    - LOGGING__LEVEL=DEBUG (для разработки)
    ) else (
        echo ⚠️  Файл .env.example не найден
    )
)
echo.

echo [6/6] Применение миграций базы данных...
alembic upgrade head
if errorlevel 1 (
    echo ⚠️  Ошибка применения миграций
    echo Это может быть нормально, если база данных ещё не создана
    echo Попробуйте запустить вручную: alembic upgrade head
)
echo.

echo ========================================
echo   ✅ НАСТРОЙКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Откройте файл .env и укажите BOT__TOKEN
echo 2. Запустите бота: uvicorn src.main:app --reload
echo    или нажмите F5 в VSCode
echo.
echo Админка будет доступна по адресу:
echo http://localhost:8000/admin
echo.
pause




