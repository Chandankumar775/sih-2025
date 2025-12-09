@echo off
echo ============================================================
echo  🛡️ RakshaNetra - AI Cybersecurity Platform
echo  Team UrbanDons - SIH 2025
echo ============================================================
echo.

REM Kill any existing processes on ports 8000 and 8080
echo [1/4] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /F /PID %%a >nul 2>&1
timeout /t 1 /nobreak > nul

echo [2/4] Starting Backend Server (Python)...
start "RakshaNetra Backend" cmd /k "cd backend && ..\backend\venv\Scripts\python.exe server.py"
echo     Backend starting at http://localhost:8000
timeout /t 5 /nobreak > nul

echo [3/4] Starting Frontend Server (React)...
start "RakshaNetra Frontend" cmd /k "npm run dev"
echo     Frontend starting at http://localhost:8080
timeout /t 3 /nobreak > nul

echo.
echo [4/4] ✅ All services started!
echo ============================================================
echo  📱 Frontend: http://localhost:8080
echo  🔌 Backend API: http://localhost:8000
echo  📚 API Docs: http://localhost:8000/docs
echo ============================================================
echo.
echo Press any key to open the application in your browser...
pause >nul
start http://localhost:8080
