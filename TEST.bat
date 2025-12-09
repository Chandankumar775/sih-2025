@echo off
echo ============================================================
echo  🧪 RakshaNetra System Test
echo ============================================================
echo.

echo [1/5] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    pause
    exit /b 1
)
echo ✅ Python OK
echo.

echo [2/5] Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js not found!
    pause
    exit /b 1
)
echo ✅ Node.js OK
echo.

echo [3/5] Checking Python packages...
cd backend
.\venv\Scripts\python -c "import fastapi, google.generativeai, uvicorn; print('✅ Core packages OK')"
if %errorlevel% neq 0 (
    echo ❌ Python packages missing! Run: pip install -r requirements.txt
    pause
    exit /b 1
)
cd ..
echo.

echo [4/5] Checking Node packages...
if not exist "node_modules" (
    echo ❌ Node modules missing! Run: npm install --legacy-peer-deps
    pause
    exit /b 1
)
echo ✅ Node modules OK
echo.

echo [5/5] Checking .env configuration...
if not exist "backend\.env" (
    echo ❌ .env file missing!
    pause
    exit /b 1
)
findstr "GOOGLE_API_KEY" backend\.env >nul
if %errorlevel% neq 0 (
    echo ❌ GOOGLE_API_KEY not configured in .env!
    pause
    exit /b 1
)
echo ✅ Configuration OK
echo.

echo ============================================================
echo  ✅ ALL TESTS PASSED!
echo  You can now run RUN.bat to start the application
echo ============================================================
pause
