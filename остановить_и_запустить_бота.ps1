# Останавливает процесс на порту 8000 (если есть) и запускает бота.
# Запуск: в PowerShell из папки проекта: .\остановить_и_запустить_бота.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UNIBOT: остановка старого и запуск" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Найти и завершить процесс, слушающий порт 8000
$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connections) {
    $pids = $connections.OwningProcess | Sort-Object -Unique
    foreach ($pid in $pids) {
        $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Останавливаю процесс на порту 8000: PID $pid ($($proc.ProcessName))" -ForegroundColor Yellow
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        }
    }
    Write-Host "Готово. Запускаю бота..." -ForegroundColor Green
} else {
    Write-Host "Порт 8000 свободен. Запускаю бота..." -ForegroundColor Green
}
Write-Host ""

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Ошибка: не найден .venv\Scripts\python.exe. Создайте виртуальное окружение." -ForegroundColor Red
    exit 1
}

& $venvPython -m uvicorn src.main:app --reload --reload-dir src --host 0.0.0.0 --port 8000









