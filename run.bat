@echo off
echo ========================================================
echo  Starting Weather-Aware Truck Routing Application
echo ========================================================

echo Starting Django Backend on http://127.0.0.1:8000 ...
start "Truck Router Backend (Django)" cmd /k "cd /d %~dp0backend && python manage.py runserver 0.0.0.0:8000"

timeout /t 2 /nobreak > nul

echo Starting React Frontend on http://localhost:5173 ...
start "Truck Router Frontend (Vite React)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================================
echo  Both services launched in new terminal windows!
echo  Open your browser at: http://localhost:5173
echo ========================================================
pause
