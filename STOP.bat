@echo off
title RakshaNetra - Stop All Servers
color 0C
echo ============================================================
echo  Stopping All RakshaNetra Servers
echo ============================================================
echo.

echo Killing processes on port 8000 (Backend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)

echo Killing processes on port 8080 (Frontend)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo ============================================================
echo  All servers stopped successfully!
echo ============================================================
echo.
pause
