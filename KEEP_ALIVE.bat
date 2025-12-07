@echo off
title RakshaNetra - Auto Restart Monitor
color 0A
echo ============================================================
echo  RakshaNetra Auto-Restart Monitor
echo  This will keep both servers running automatically
echo ============================================================
echo.

:MONITOR_LOOP

REM Check backend
netstat -ano | findstr :8000 > nul
if %errorlevel% neq 0 (
    echo [%date% %time%] Backend stopped! Restarting...
    start "RakshaNetra Backend" /MIN cmd /k "cd backend && C:\Users\CHANDAN\AppData\Local\Programs\Python\Python313\python.exe server.py"
    timeout /t 3 /nobreak > nul
)

REM Check frontend
netstat -ano | findstr :8080 > nul
if %errorlevel% neq 0 (
    echo [%date% %time%] Frontend stopped! Restarting...
    start "RakshaNetra Frontend" /MIN cmd /k "npm run dev"
    timeout /t 5 /nobreak > nul
)

REM Wait 10 seconds before checking again
timeout /t 10 /nobreak > nul
goto MONITOR_LOOP
