# Ubrat .env iz Git i pushit bez sekretov.
# Zapusk: .\ispravit_git_i_zapushit.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ubrat .env iz Git i push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Ubirayu .env iz indeksa Git..." -ForegroundColor Yellow
git rm --cached .env 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   .env uzhe ne v indekse." -ForegroundColor Gray
}

Write-Host "2. Ispravlyayu posledniy kommit bez .env..." -ForegroundColor Yellow
git add -A
git reset HEAD .env 2>$null
git status -s
git commit --amend --no-edit
if ($LASTEXITCODE -ne 0) {
    Write-Host "Oshibka pri amend." -ForegroundColor Red
    exit 1
}

Write-Host "3. Otpravlyayu na GitHub..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push ne proshel." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Gotovo. Sinhronizaciya s GitHub vypolnena." -ForegroundColor Green
Write-Host "V Cursor nazhmi obnovleniye v paneli Source Control." -ForegroundColor Gray





