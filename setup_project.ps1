# Скрипт настройки проекта Unibot
# Кодировка UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  НАСТРОЙКА ПРОЕКТА UNIBOT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Переходим в директорию скрипта
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# [1/6] Проверка Python 3.11
Write-Host "[1/6] Проверка Python 3.11..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python не найден"
    }
    if ($pythonVersion -notmatch "3\.11") {
        Write-Host "⚠️  Найден Python, но не версия 3.11" -ForegroundColor Red
        Write-Host $pythonVersion -ForegroundColor Red
        Write-Host ""
        Write-Host "Установите Python 3.11 с официального сайта:" -ForegroundColor Yellow
        Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    Write-Host $pythonVersion -ForegroundColor Green
    Write-Host "✅ Python 3.11 найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не найден в PATH!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Установите Python 3.11 с официального сайта:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ВАЖНО: При установке отметьте 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# [2/6] Создание виртуального окружения
Write-Host "[2/6] Создание виртуального окружения..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️  Виртуальное окружение уже существует" -ForegroundColor Yellow
    Write-Host "Удаляю старое окружение..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка создания виртуального окружения!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Виртуальное окружение создано" -ForegroundColor Green
Write-Host ""

# [3/6] Активация и обновление pip
Write-Host "[3/6] Активация виртуального окружения и обновление pip..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка обновления pip!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ pip обновлён" -ForegroundColor Green
Write-Host ""

# [4/6] Установка зависимостей
Write-Host "[4/6] Установка зависимостей..." -ForegroundColor Yellow
Write-Host "Это может занять несколько минут..." -ForegroundColor Gray
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка установки зависимостей из requirements.txt!" -ForegroundColor Red
    exit 1
}
pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка установки зависимостей из requirements-dev.txt!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Все зависимости установлены" -ForegroundColor Green
Write-Host ""

# [5/6] Настройка .env
Write-Host "[5/6] Настройка файла .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  Файл .env уже существует" -ForegroundColor Yellow
    Write-Host "Пропускаю копирование .env.example" -ForegroundColor Gray
} else {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Файл .env создан из .env.example" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  ВАЖНО: Откройте файл .env и укажите:" -ForegroundColor Yellow
        Write-Host "   - BOT__TOKEN=ваш_токен_бота" -ForegroundColor Yellow
        Write-Host "   - LOGGING__LEVEL=DEBUG (для разработки)" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  Файл .env.example не найден" -ForegroundColor Yellow
    }
}
Write-Host ""

# [6/6] Применение миграций
Write-Host "[6/6] Применение миграций базы данных..." -ForegroundColor Yellow
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Ошибка применения миграций" -ForegroundColor Yellow
    Write-Host "Это может быть нормально, если база данных ещё не создана" -ForegroundColor Gray
    Write-Host "Попробуйте запустить вручную: alembic upgrade head" -ForegroundColor Gray
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ НАСТРОЙКА ЗАВЕРШЕНА!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. Откройте файл .env и укажите BOT__TOKEN" -ForegroundColor White
Write-Host "2. Запустите бота: uvicorn src.main:app --reload" -ForegroundColor White
Write-Host "   или нажмите F5 в VSCode" -ForegroundColor White
Write-Host ""
Write-Host "Админка будет доступна по адресу:" -ForegroundColor Yellow
Write-Host "http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""




