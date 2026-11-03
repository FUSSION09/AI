# Apex Autonomous System: Server & Dashboard Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " LAUNCHING APEX AUTONOMOUS SYSTEM (UAS) SERVICE MESH GATEWAY" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Web HUD Dashboard:   http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Interactive API Doc: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Metrics Scrape:      http://127.0.0.1:8000/metrics" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

python d:\AI\main.py start-gateway

