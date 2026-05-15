# Backend ve Frontend'i ayri terminallerde baslat

$projectRoot = Get-Location
$backendPath = Join-Path $projectRoot "churn-backend"
$frontendPath = Join-Path $projectRoot "churn-frontend"

Write-Host "Backend baslatiliyor (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd '$backendPath'; .\.venv\Scripts\uvicorn.exe main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "Frontend baslatiliyor (http://localhost:5173)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit', '-Command', "cd '$frontendPath'; npm run dev"

Write-Host ""
Write-Host "Hazir! Tarayicida ac: http://localhost:5173" -ForegroundColor Green
