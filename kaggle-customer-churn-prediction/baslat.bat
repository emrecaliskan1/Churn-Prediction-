@echo off
chcp 65001 >nul

echo Backend baslatiliyor (http://localhost:8000)...
start "Backend" cmd /k "cd churn-backend && .venv\Scripts\uvicorn.exe main:app --reload --port 8000"

timeout /t 2 /nobreak

echo Frontend baslatiliyor (http://localhost:5173)...
start "Frontend" cmd /k "cd churn-frontend && npm run dev"

echo.
echo Hazir! Tarayicida ac: http://localhost:5173
pause
