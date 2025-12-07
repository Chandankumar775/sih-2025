@echo off
echo ============================================================
echo  Starting RakshaNetra Defence-Grade Cybersecurity Platform
echo ============================================================
echo.

REM Check if backend is already running on port 8000
echo [1/3] Checking backend status...
netstat -ano | findstr :8000 > nul
if %errorlevel% equ 0 (
    echo Backend already running on port 8000
) else (
    echo [2/3] Starting Backend Server on port 8000...
    start "RakshaNetra Backend" cmd /k "cd backend && C:\Users\CHANDAN\AppData\Local\Programs\Python\Python313\python.exe server.py"
    timeout /t 3 /nobreak > nul
)

echo.
echo [3/3] Starting Frontend Server on port 8080...
start "RakshaNetra Frontend" cmd /k "npm run dev"

timeout /t 2 /nobreak > nul
echo.
echo ============================================================
echo  RakshaNetra Started Successfully!
echo ============================================================
echo  Backend API: http://localhost:8000
echo  API Docs:    http://localhost:8000/docs
echo  Frontend:    http://localhost:8080
echo ============================================================
echo.
echo Opening website in browser...
timeout /t 3 /nobreak > nul
start http://localhost:8080

echo.
echo Press any key to close this window (servers will keep running)...
pause > nul
