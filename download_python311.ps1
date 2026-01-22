# Скрипт для скачивания и установки Python 3.11
# Требует прав администратора

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  УСТАНОВКА PYTHON 3.11" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  Для установки требуются права администратора" -ForegroundColor Yellow
    Write-Host "Запустите PowerShell от имени администратора" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Или установите Python 3.11 вручную:" -ForegroundColor Yellow
    Write-Host "1. Скачайте: https://www.python.org/downloads/release/python-31111/" -ForegroundColor Cyan
    Write-Host "2. Запустите установщик" -ForegroundColor Cyan
    Write-Host "3. Отметьте 'Add Python to PATH'" -ForegroundColor Cyan
    exit 1
}

# URL для скачивания Python 3.11.11 (64-bit)
$pythonUrl = "https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe"
$installerPath = "$env:TEMP\python-3.11.11-amd64.exe"

Write-Host "[1/3] Скачивание Python 3.11.11..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✅ Установщик скачан" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка скачивания: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Скачайте вручную:" -ForegroundColor Yellow
    Write-Host $pythonUrl -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "[2/3] Запуск установщика..." -ForegroundColor Yellow
Write-Host "⚠️  В открывшемся окне установки:" -ForegroundColor Yellow
Write-Host "   1. Отметьте 'Add Python to PATH' внизу окна" -ForegroundColor White
Write-Host "   2. Нажмите 'Install Now'" -ForegroundColor White
Write-Host ""

# Запуск установщика
Start-Process -FilePath $installerPath -Wait

Write-Host ""
Write-Host "[3/3] Проверка установки..." -ForegroundColor Yellow

# Проверка через py launcher
$python311 = Get-Command py -ErrorAction SilentlyContinue
if ($python311) {
    $version = & py -3.11 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 3.11 установлен: $version" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Python 3.11 может быть установлен, но не добавлен в PATH" -ForegroundColor Yellow
        Write-Host "   Перезапустите командную строку и проверьте: py -3.11 --version" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Python Launcher не найден" -ForegroundColor Yellow
    Write-Host "   Проверьте установку вручную" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  УСТАНОВКА ЗАВЕРШЕНА" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. Перезапустите командную строку" -ForegroundColor White
Write-Host "2. Проверьте: py -3.11 --version" -ForegroundColor White
Write-Host "3. Создайте виртуальное окружение: py -3.11 -m venv .venv" -ForegroundColor White
Write-Host ""




