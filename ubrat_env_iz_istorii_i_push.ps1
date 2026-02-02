# Udalyaet .env iz VSEY istorii kommitov (ot origin/main do HEAD) i delaet force push.
# Zapusk: .\ubrat_env_iz_istorii_i_push.ps1
# Vnimanie: perepisyvayet istoriyu. Esli kto-to uzhe tyanul etu vetku - u nih budut konflikty.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Udalyaem .env iz vsey istorii" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Fetch origin..." -ForegroundColor Yellow
git fetch origin
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "2. Udalyaem .env iz vseh kommitov (origin/main..HEAD)..." -ForegroundColor Yellow
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty origin/main..HEAD
if ($LASTEXITCODE -ne 0) {
    Write-Host "Oshibka filter-branch." -ForegroundColor Red
    exit 1
}

Write-Host "3. Force push na GitHub..." -ForegroundColor Yellow
git push --force origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push ne proshel." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Gotovo. Istoriya perepisana, .env ubran, push vypolnen." -ForegroundColor Green






