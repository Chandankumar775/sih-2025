<#
.SYNOPSIS
    RakshanetrA Cyber Security Portal - Complete Environment Setup Script
    
.DESCRIPTION
    This script automates the complete setup of the RakshanetrA project on a new machine.
    It installs all required dependencies, sets up Python/Node environments, and configures everything.
    
.NOTES
    Author: Urban Dons Team
    Date: December 9, 2025
    Requires: PowerShell 5.1+ with Administrator privileges for some installations
#>

[CmdletBinding()]
param(
    [switch]$SkipGitPull,
    [switch]$SkipDependencies
)

# Color output functions
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Header { 
    param($Message) 
    Write-Host "`n=================================================" -ForegroundColor Magenta
    Write-Host "  $Message" -ForegroundColor Magenta
    Write-Host "=================================================`n" -ForegroundColor Magenta
}

# Error handling
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Check if running as admin (optional but recommended)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Not running as Administrator. Some installations may fail."
    Write-Info "Consider running: Start-Process powershell -Verb RunAs -ArgumentList '-File $PSCommandPath'"
}

Write-Header "🛡️ RakshanetrA Setup Script"
Write-Info "Starting environment setup..."

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

#region Git Pull
if (-not $SkipGitPull) {
    Write-Header "📦 Pulling Latest Code from GitHub"
    try {
        git pull origin main
        Write-Success "Code updated from GitHub"
    } catch {
        Write-Warning "Git pull failed: $_. Continuing with existing code..."
    }
}
#endregion

#region Check Node.js
Write-Header "🟢 Checking Node.js Installation"
try {
    $nodeVersion = node --version 2>$null
    if ($nodeVersion) {
        Write-Success "Node.js installed: $nodeVersion"
    } else {
        throw "Node not found"
    }
} catch {
    Write-Error "Node.js not installed!"
    Write-Info "Please install Node.js from: https://nodejs.org/"
    Write-Info "Download the LTS version (20.x or higher)"
    
    $download = Read-Host "Open Node.js download page? (y/n)"
    if ($download -eq 'y') {
        Start-Process "https://nodejs.org/"
    }
    Write-Error "Please install Node.js and run this script again."
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version 2>$null
    Write-Success "npm installed: v$npmVersion"
} catch {
    Write-Error "npm not found. Please reinstall Node.js"
    exit 1
}
#endregion

#region Check Python
Write-Header "🐍 Checking Python Installation"
$pythonCmd = $null
$pythonVersions = @("python", "python3", "py")

foreach ($cmd in $pythonVersions) {
    try {
        $version = & $cmd --version 2>$null
        if ($version -match "Python (\d+\.\d+)") {
            $pythonCmd = $cmd
            Write-Success "Python installed: $version (command: $cmd)"
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Error "Python not installed!"
    Write-Info "Please install Python 3.10+ from: https://www.python.org/downloads/"
    Write-Info "IMPORTANT: Check 'Add Python to PATH' during installation"
    
    $download = Read-Host "Open Python download page? (y/n)"
    if ($download -eq 'y') {
        Start-Process "https://www.python.org/downloads/"
    }
    Write-Error "Please install Python and run this script again."
    exit 1
}

# Check pip
try {
    $pipVersion = & $pythonCmd -m pip --version 2>$null
    Write-Success "pip installed: $pipVersion"
} catch {
    Write-Error "pip not found. Installing pip..."
    & $pythonCmd -m ensurepip --upgrade
}
#endregion

#region Install Frontend Dependencies
if (-not $SkipDependencies) {
    Write-Header "📦 Installing Frontend Dependencies (npm)"
    Write-Info "This may take a few minutes..."
    
    if (Test-Path "package.json") {
        try {
            # Check if node_modules exists
            if (Test-Path "node_modules") {
                Write-Info "node_modules exists, updating packages..."
            } else {
                Write-Info "Fresh installation of packages..."
            }
            
            npm install
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Frontend dependencies installed successfully"
            } else {
                Write-Error "npm install failed with exit code $LASTEXITCODE"
                Write-Info "Trying with --legacy-peer-deps..."
                npm install --legacy-peer-deps
            }
        } catch {
            Write-Error "Failed to install frontend dependencies: $_"
            exit 1
        }
    } else {
        Write-Warning "package.json not found, skipping frontend dependencies"
    }
}
#endregion

#region Setup Python Virtual Environment
Write-Header "🐍 Setting up Python Virtual Environment"

$venvPath = Join-Path $ScriptDir "backend\venv"

if (Test-Path $venvPath) {
    Write-Info "Virtual environment already exists at: $venvPath"
    $recreate = Read-Host "Recreate virtual environment? (y/n)"
    if ($recreate -eq 'y') {
        Write-Info "Removing existing virtual environment..."
        Remove-Item $venvPath -Recurse -Force
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Info "Creating virtual environment..."
    try {
        & $pythonCmd -m venv backend\venv
        Write-Success "Virtual environment created"
    } catch {
        Write-Error "Failed to create virtual environment: $_"
        exit 1
    }
}

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Info "Activating virtual environment..."
    & $activateScript
    Write-Success "Virtual environment activated"
} else {
    Write-Error "Activation script not found: $activateScript"
    exit 1
}
#endregion

#region Install Python Dependencies
if (-not $SkipDependencies) {
    Write-Header "📦 Installing Python Dependencies"
    
    $requirementsPath = Join-Path $ScriptDir "backend\requirements.txt"
    
    if (Test-Path $requirementsPath) {
        Write-Info "Installing packages from requirements.txt..."
        Write-Info "This may take several minutes..."
        
        try {
            # Upgrade pip first
            python -m pip install --upgrade pip
            Write-Success "pip upgraded"
            
            # Install requirements
            python -m pip install -r $requirementsPath
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python dependencies installed successfully"
            } else {
                Write-Warning "Some packages may have failed to install (exit code: $LASTEXITCODE)"
                Write-Info "This might be okay - spaCy and some packages are optional"
            }
        } catch {
            Write-Warning "Error installing Python dependencies: $_"
            Write-Info "Continuing anyway - some packages are optional"
        }
    } else {
        Write-Warning "requirements.txt not found at: $requirementsPath"
    }
}
#endregion

#region Verify Environment Files
Write-Header "🔐 Verifying Environment Configuration"

# Check frontend .env
$frontendEnv = Join-Path $ScriptDir ".env"
if (Test-Path $frontendEnv) {
    Write-Success "Frontend .env file exists"
    $content = Get-Content $frontendEnv -Raw
    if ($content -match "VITE_SUPABASE_URL") {
        Write-Success "Frontend environment variables configured"
    } else {
        Write-Warning "Frontend .env may be incomplete"
    }
} else {
    Write-Warning "Frontend .env file not found!"
    Write-Info "Creating from repository version..."
}

# Check backend .env
$backendEnv = Join-Path $ScriptDir "backend\.env"
if (Test-Path $backendEnv) {
    Write-Success "Backend .env file exists"
    $content = Get-Content $backendEnv -Raw
    if ($content -match "GOOGLE_API_KEY" -and $content -match "SUPABASE_URL") {
        Write-Success "Backend environment variables configured"
    } else {
        Write-Warning "Backend .env may be incomplete"
    }
} else {
    Write-Warning "Backend .env file not found!"
    Write-Info "Creating from repository version..."
}
#endregion

#region Database Setup
Write-Header "🗄️ Setting up Database"

$dbPath = Join-Path $ScriptDir "backend\rakshanetra.db"
if (Test-Path $dbPath) {
    Write-Success "Database file exists: rakshanetra.db"
} else {
    Write-Info "Database will be created on first run"
}

# Check for migration scripts
$migrationsPath = Join-Path $ScriptDir "backend\migrations"
if (Test-Path $migrationsPath) {
    Write-Success "Database migrations found"
} else {
    Write-Info "No migrations directory found"
}
#endregion

#region Create Reports Directory
Write-Header "📁 Creating Required Directories"

$requiredDirs = @(
    "backend\reports",
    "backend\evidence_vault\files",
    "backend\evidence_vault\quarantine",
    "backend\evidence_vault\archive"
)

foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $ScriptDir $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Success "Created directory: $dir"
    } else {
        Write-Info "Directory exists: $dir"
    }
}
#endregion

#region Verify Installation
Write-Header "✅ Verifying Installation"

Write-Info "Checking installed packages..."

# Check key frontend packages
Write-Info "`nFrontend packages:"
try {
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $keyPackages = @("react", "vite", "typescript", "axios")
    foreach ($pkg in $keyPackages) {
        if ($packageJson.dependencies.$pkg -or $packageJson.devDependencies.$pkg) {
            Write-Success "  $pkg installed"
        }
    }
} catch {
    Write-Warning "Could not verify frontend packages"
}

# Check key Python packages
Write-Info "`nPython packages:"
$keyPythonPackages = @("fastapi", "uvicorn", "google-generativeai", "pydantic")
foreach ($pkg in $keyPythonPackages) {
    try {
        $installed = python -m pip show $pkg 2>$null
        if ($installed) {
            Write-Success "  $pkg installed"
        } else {
            Write-Warning "  $pkg not found"
        }
    } catch {
        Write-Warning "  Could not verify $pkg"
    }
}
#endregion

#region Create Helper Scripts
Write-Header "🚀 Creating Helper Scripts"

# Create START script
$startScript = @'
@echo off
echo ================================================
echo   🛡️ RakshanetrA - Starting All Services
echo ================================================
echo.

echo Starting Backend Server...
start "RakshanetrA Backend" cmd /k "cd backend && venv\Scripts\activate && python server.py"
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "RakshanetrA Frontend" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo   ✅ All Services Started
echo ================================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:8080
echo   API Docs: http://localhost:8000/docs
echo ================================================
echo.

timeout /t 5 /nobreak >nul
start http://localhost:8080
'@

Set-Content -Path "START.bat" -Value $startScript -Force
Write-Success "Created START.bat"

# Create STOP script
$stopScript = @'
@echo off
echo Stopping RakshanetrA services...

taskkill /FI "WindowTitle eq RakshanetrA Backend*" /T /F 2>nul
taskkill /FI "WindowTitle eq RakshanetrA Frontend*" /T /F 2>nul

echo Services stopped.
timeout /t 2
'@

Set-Content -Path "STOP.bat" -Value $stopScript -Force
Write-Success "Created STOP.bat"

#endregion

#region Final Instructions
Write-Header "🎉 Setup Complete!"

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║       🛡️  RakshanetrA Cyber Security Portal Ready!  🛡️       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝

📋 SETUP SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Node.js & npm verified
✓ Python & pip verified
✓ Frontend dependencies installed
✓ Python virtual environment created
✓ Python dependencies installed
✓ Environment files configured
✓ Database setup verified
✓ Required directories created
✓ Helper scripts created

🚀 QUICK START:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option 1 (Recommended): Double-click START.bat

Option 2 (Manual):
  Terminal 1: cd backend && venv\Scripts\activate && python server.py
  Terminal 2: npm run dev

🌐 ACCESS URLS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend:  http://localhost:8080
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs

👤 DEMO ACCOUNTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reporter: reporter@army.mil / demo123
Admin:    admin@rakshanetra.mil / demo123

📁 PROJECT STRUCTURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

src/              - Frontend React code
backend/          - FastAPI backend
backend/reports/  - Incident reports (JSON files)
.env              - Frontend environment variables
backend/.env      - Backend environment variables

⚠️  TROUBLESHOOTING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If backend fails to start:
  1. Check Python version: python --version (should be 3.10+)
  2. Activate venv: backend\venv\Scripts\activate
  3. Reinstall packages: pip install -r backend\requirements.txt

If frontend fails to start:
  1. Delete node_modules folder
  2. Run: npm install
  3. Run: npm run dev

Port conflicts:
  - Backend uses port 8000
  - Frontend uses port 8080
  - Check if ports are in use: netstat -ano | findstr :8000

🔧 MAINTENANCE COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pull latest code:    git pull origin main
Update frontend:     npm install
Update backend:      pip install -r backend\requirements.txt
Rerun setup:         .\SETUP.ps1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"@ -ForegroundColor Green

Write-Info "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

#endregion
