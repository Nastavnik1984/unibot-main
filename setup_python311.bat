@echo off
chcp 65001 >nul
title Установка Python 3.11
color 0B
echo ========================================
echo   УСТАНОВКА PYTHON 3.11
echo ========================================
echo.

echo Этот скрипт поможет установить Python 3.11
echo.
echo Выберите способ установки:
echo   1. Скачать установщик и открыть его (рекомендуется)
echo   2. Показать инструкцию по ручной установке
echo   3. Выход
echo.
set /p choice="Ваш выбор (1-3): "

if "%choice%"=="1" goto download
if "%choice%"=="2" goto manual
if "%choice%"=="3" goto end
goto download

:download
echo.
echo [1/2] Скачивание установщика Python 3.11.11...
echo Это может занять несколько минут...
echo.

powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe' -OutFile '%TEMP%\python-3.11.11-amd64.exe' -UseBasicParsing"

if errorlevel 1 (
    echo ❌ Ошибка скачивания
    echo.
    echo Скачайте вручную:
    echo https://www.python.org/downloads/release/python-31111/
    pause
    exit /b 1
)

echo ✅ Установщик скачан
echo.
echo [2/2] Запуск установщика...
echo.
echo ⚠️  ВАЖНО: В открывшемся окне установки:
echo    1. Отметьте "Add Python to PATH" внизу окна
echo    2. Нажмите "Install Now"
echo.
pause

start "" "%TEMP%\python-3.11.11-amd64.exe"

echo.
echo Установщик запущен. Дождитесь завершения установки.
echo.
echo После установки:
echo   1. Перезапустите командную строку
echo   2. Проверьте: py -3.11 --version
echo   3. Создайте виртуальное окружение: py -3.11 -m venv .venv
echo.
pause
goto end

:manual
echo.
echo ========================================
echo   ИНСТРУКЦИЯ ПО РУЧНОЙ УСТАНОВКЕ
echo ========================================
echo.
echo 1. Откройте в браузере:
echo    https://www.python.org/downloads/release/python-31111/
echo.
echo 2. Прокрутите вниз до раздела "Files"
echo.
echo 3. Скачайте "Windows installer (64-bit)"
echo    Или прямую ссылку:
echo    https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe
echo.
echo 4. Запустите скачанный файл
echo.
echo 5. ВАЖНО: Отметьте "Add Python to PATH" внизу окна
echo.
echo 6. Нажмите "Install Now"
echo.
echo 7. Дождитесь завершения установки
echo.
echo 8. Перезапустите командную строку
echo.
echo 9. Проверьте установку:
echo    py -3.11 --version
echo.
pause
goto end

:end
exit /b 0




