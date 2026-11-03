Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting Weather-Aware Truck Routing App" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Django Backend in a separate process
Write-Host "Starting Django Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\backend'; python manage.py runserver 0.0.0.0:8000"

Start-Sleep -Seconds 2

# 2. Start Frontend Dev Server in a separate process
Write-Host "Starting React Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\frontend'; npm run dev"

Write-Host ""
Write-Host "Both services are running in separate terminal windows." -ForegroundColor Yellow
Write-Host "Open your browser at: http://localhost:5173" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
