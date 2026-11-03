# Apex UAS One-Click Launcher
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Starting Apex Autonomous System (UAS) Gateway..." -ForegroundColor Green
Write-Host "Web UI:        http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Swagger Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan
python main.py start-gateway --host 0.0.0.0 --port 8000

