# Автоматическая установка Python 3.11 с параметрами тихой установки
# Требует прав администратора

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  АВТОМАТИЧЕСКАЯ УСТАНОВКА PYTHON 3.11" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️  Для установки требуются права администратора" -ForegroundColor Yellow
    Write-Host "Запустите PowerShell от имени администратора" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Или запустите: setup_python311.bat" -ForegroundColor Cyan
    exit 1
}

# URL для скачивания Python 3.11.11 (64-bit)
$pythonUrl = "https://www.python.org/ftp/python/3.11.11/python-3.11.11-amd64.exe"
$installerPath = "$env:TEMP\python-3.11.11-amd64.exe"

Write-Host "[1/4] Проверка наличия Python 3.11..." -ForegroundColor Yellow
$python311 = Get-Command py -ErrorAction SilentlyContinue
if ($python311) {
    $version = & py -3.11 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 3.11 уже установлен: $version" -ForegroundColor Green
        Write-Host ""
        Write-Host "Проверка завершена. Python 3.11 готов к использованию." -ForegroundColor Green
        exit 0
    }
}
Write-Host "Python 3.11 не найден, продолжаем установку..." -ForegroundColor Yellow
Write-Host ""

Write-Host "[2/4] Скачивание установщика Python 3.11.11..." -ForegroundColor Yellow
Write-Host "Это может занять несколько минут..." -ForegroundColor Gray

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✅ Установщик скачан: $installerPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка скачивания: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Скачайте вручную:" -ForegroundColor Yellow
    Write-Host $pythonUrl -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "[3/4] Установка Python 3.11.11..." -ForegroundColor Yellow
Write-Host "Это может занять несколько минут..." -ForegroundColor Gray

# Параметры для тихой установки:
# /quiet - тихая установка без окон
# InstallAllUsers=1 - установка для всех пользователей
# PrependPath=1 - добавление в PATH
# Include_test=0 - не устанавливать тесты
# Include_doc=0 - не устанавливать документацию
$installArgs = @(
    "/quiet",
    "InstallAllUsers=1",
    "PrependPath=1",
    "Include_test=0",
    "Include_doc=0",
    "Include_launcher=1"
)

try {
    $process = Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Установка завершена успешно" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Установка завершена с кодом: $($process.ExitCode)" -ForegroundColor Yellow
        Write-Host "Проверяем установку..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ошибка при установке: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/4] Проверка установки..." -ForegroundColor Yellow

# Обновляем переменные окружения
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Небольшая задержка для применения изменений
Start-Sleep -Seconds 2

# Проверка через py launcher
$python311Check = Get-Command py -ErrorAction SilentlyContinue
if ($python311Check) {
    $version = & py -3.11 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python 3.11 успешно установлен: $version" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Python установлен, но требуется перезапуск командной строки" -ForegroundColor Yellow
        Write-Host "   Перезапустите PowerShell и проверьте: py -3.11 --version" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Python Launcher не найден" -ForegroundColor Yellow
    Write-Host "   Может потребоваться перезапуск системы" -ForegroundColor Yellow
}

# Проверка через python3.11
$python311Exe = Get-Command python3.11 -ErrorAction SilentlyContinue
if (-not $python311Exe) {
    $python311Exe = Get-Command python -ErrorAction SilentlyContinue
    if ($python311Exe) {
        $version = & python --version 2>&1
        if ($version -match "3\.11") {
            Write-Host "✅ Python 3.11 найден через python: $version" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  ✅ УСТАНОВКА ЗАВЕРШЕНА" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. Перезапустите командную строку/PowerShell" -ForegroundColor White
Write-Host "2. Проверьте установку:" -ForegroundColor White
Write-Host "   py -3.11 --version" -ForegroundColor Cyan
Write-Host "   или" -ForegroundColor Gray
Write-Host "   python3.11 --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Создайте виртуальное окружение:" -ForegroundColor White
Write-Host "   py -3.11 -m venv .venv" -ForegroundColor Cyan
Write-Host "   или запустите:" -ForegroundColor Gray
Write-Host "   recreate_venv_python311.bat" -ForegroundColor Cyan
Write-Host ""

# Удаление временного файла
if (Test-Path $installerPath) {
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
}

