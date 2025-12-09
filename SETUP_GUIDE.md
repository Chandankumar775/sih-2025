# 🛡️ RakshanetrA - Complete Setup Guide

**Cyber Security Portal for Ministry of Defence, Government of India**

This guide will help you set up the complete RakshanetrA development environment on a new machine.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup (Recommended)](#quick-setup-recommended)
- [Manual Setup](#manual-setup)
- [Running the Application](#running-the-application)
- [Demo Accounts](#demo-accounts)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

Before running the setup script, ensure you have:

### Required Software

1. **Node.js 20.x or higher**
   - Download: https://nodejs.org/
   - ✅ Check 'Add to PATH' during installation
   - Verify: `node --version`

2. **Python 3.10 or higher**
   - Download: https://www.python.org/downloads/
   - ✅ Check 'Add Python to PATH' during installation
   - Verify: `python --version`

3. **Git**
   - Download: https://git-scm.com/
   - Configure: 
     ```bash
     git config --global user.name "Your Name"
     git config --global user.email "your.email@example.com"
     ```

### Optional (Recommended)

- **PowerShell 5.1+** (Windows) - Usually pre-installed
- **Administrator Privileges** - For some installations

---

## 🚀 Quick Setup (Recommended)

This is the **fastest and easiest** way to set up everything:

### Step 1: Clone Repository

```powershell
# Clone the repository
git clone https://github.com/Chandankumar775/sih-2025.git

# Navigate to project directory
cd sih-2025
```

### Step 2: Run Setup Script

```powershell
# Right-click SETUP.ps1 and select "Run with PowerShell"
# OR run from PowerShell:
.\SETUP.ps1
```

The setup script will automatically:
- ✅ Verify Node.js and Python installations
- ✅ Install all frontend dependencies (npm packages)
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies (pip packages)
- ✅ Set up environment variables
- ✅ Create required directories
- ✅ Create START.bat and STOP.bat helper scripts
- ✅ Verify database configuration

### Step 3: Start Application

```powershell
# Option 1: Double-click START.bat
START.bat

# Option 2: Run from PowerShell
.\START.bat
```

**That's it!** The application will open in your browser automatically.

---

## 🔧 Manual Setup

If you prefer to set up manually or the script fails:

### 1. Install Frontend Dependencies

```powershell
# In project root directory
npm install
```

If you encounter errors:
```powershell
npm install --legacy-peer-deps
```

### 2. Set Up Python Virtual Environment

```powershell
# Create virtual environment
python -m venv backend\venv

# Activate virtual environment (Windows)
backend\venv\Scripts\activate

# On macOS/Linux:
# source backend/venv/bin/activate
```

### 3. Install Python Dependencies

```powershell
# Make sure virtual environment is activated
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

### 4. Verify Environment Files

The repository includes all environment files (`.env`). Verify they exist:

- Root directory: `.env` (Frontend config)
- Backend directory: `backend\.env` (Backend config)

### 5. Create Required Directories

```powershell
# Create directories
mkdir backend\reports
mkdir backend\evidence_vault\files
mkdir backend\evidence_vault\quarantine
mkdir backend\evidence_vault\archive
```

---

## 🎮 Running the Application

### Option 1: Using Helper Scripts (Easiest)

```powershell
# Start everything
.\START.bat

# Stop everything
.\STOP.bat
```

### Option 2: Manual Start

**Terminal 1 (Backend):**
```powershell
cd backend
venv\Scripts\activate
python server.py
```

**Terminal 2 (Frontend):**
```powershell
npm run dev
```

### Access Points

Once running, access the application at:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8080 | Main application UI |
| **Backend API** | http://localhost:8000 | REST API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

---

## 👤 Demo Accounts

### Reporter Account
- **Email:** `reporter@army.mil`
- **Password:** `demo123`
- **Access:** Can report cyber incidents

### Admin Account
- **Email:** `admin@rakshanetra.mil`
- **Password:** `demo123`
- **Access:** Full dashboard, analytics, incident management

---

## 📁 Project Structure

```
sih-2025/
├── 📄 SETUP.ps1              # Automated setup script
├── 📄 START.bat              # Start all services
├── 📄 STOP.bat               # Stop all services
├── 📄 package.json           # Frontend dependencies
├── 📄 .env                   # Frontend environment variables
│
├── 📁 src/                   # Frontend React application
│   ├── components/           # Reusable UI components
│   ├── pages/                # Application pages
│   ├── services/             # API service layer
│   └── utils/                # Utility functions
│
├── 📁 backend/               # Python FastAPI backend
│   ├── 📄 server.py          # Main server file
│   ├── 📄 requirements.txt   # Python dependencies
│   ├── 📄 .env               # Backend environment variables
│   ├── 📄 rakshanetra.db     # SQLite database
│   │
│   ├── 📁 modules/           # Backend modules
│   │   ├── auth_manager.py   # Authentication
│   │   ├── nlp_analyzer.py   # AI/NLP analysis
│   │   ├── threat_matcher.py # Threat detection
│   │   └── evidence_vault.py # File management
│   │
│   ├── 📁 reports/           # JSON incident reports
│   └── 📁 evidence_vault/    # Uploaded files storage
│
├── 📁 public/                # Static assets
└── 📁 media/                 # Images and media files
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "Node.js not found"

**Solution:**
- Install Node.js from https://nodejs.org/
- ✅ Check "Add to PATH" during installation
- Restart PowerShell/Terminal
- Verify: `node --version`

#### 2. "Python not found"

**Solution:**
- Install Python from https://www.python.org/downloads/
- ✅ Check "Add Python to PATH" during installation
- Restart PowerShell/Terminal
- Verify: `python --version`

#### 3. Frontend won't start / Port 8080 in use

**Solution:**
```powershell
# Check what's using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in vite.config.ts
```

#### 4. Backend won't start / Port 8000 in use

**Solution:**
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

#### 5. "pip install" fails for some packages

**Solution:**
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with no cache
pip install --no-cache-dir -r backend\requirements.txt

# Some packages (like spaCy) are optional - the app will work without them
```

#### 6. Virtual environment activation fails

**Solution:**
```powershell
# If you get "execution policy" error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
backend\venv\Scripts\activate
```

#### 7. npm install fails

**Solution:**
```powershell
# Delete node_modules and package-lock.json
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force

# Clear npm cache
npm cache clean --force

# Try again with legacy peer deps
npm install --legacy-peer-deps
```

#### 8. Database errors on startup

**Solution:**
```powershell
# The database will be auto-created on first run
# If issues persist, delete and let it recreate:
Remove-Item backend\rakshanetra.db

# Restart backend server
```

#### 9. Environment variables not loaded

**Solution:**
- Verify `.env` exists in root directory
- Verify `backend\.env` exists in backend directory
- Check file contents are not empty
- Restart both frontend and backend

#### 10. "Module not found" errors in frontend

**Solution:**
```powershell
# Reinstall dependencies
npm install

# If still failing, try:
Remove-Item node_modules -Recurse -Force
npm install
```

---

## 🔄 Updating the Application

### Pull Latest Changes

```powershell
# Stop all services
.\STOP.bat

# Pull latest code
git pull origin main

# Rerun setup (to install any new dependencies)
.\SETUP.ps1

# Start services
.\START.bat
```

### Update Frontend Dependencies

```powershell
npm install
# or
npm update
```

### Update Backend Dependencies

```powershell
backend\venv\Scripts\activate
pip install -r backend\requirements.txt --upgrade
```

---

## 🔐 Security Notes

### Environment Variables

The repository includes `.env` files with **actual credentials** because:
- ✅ This is for **trusted team members only**
- ✅ Using demo/development credentials
- ✅ Not for production deployment

**For Production:**
- Create new Supabase project
- Generate new API keys
- Update `.env` files with production credentials
- **Never commit production credentials to Git**

---

## 📞 Support

If you encounter issues not covered in troubleshooting:

1. **Check the console/terminal output** for error messages
2. **Verify all prerequisites** are installed correctly
3. **Try manual setup** if automated script fails
4. **Contact team members** with:
   - Error message screenshot
   - Steps you've tried
   - Your environment (Windows/Mac/Linux, Node version, Python version)

---

## 🎓 Development Tips

### Recommended VS Code Extensions

- ESLint
- Prettier
- Python
- Pylance
- Thunder Client (API testing)

### Useful Commands

```powershell
# Frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Backend (activate venv first)
python server.py     # Start backend server
python -m pytest     # Run tests (if configured)

# Database
# SQLite database can be viewed with DB Browser for SQLite
# Download: https://sqlitebrowser.org/
```

---

## 📜 License

Ministry of Defence, Government of India
Urban Dons Team - SIH 2025

---

## 🏆 Credits

**Team Urban Dons**
- Cyber Security Portal for Defence
- Smart India Hackathon 2025

---

**Last Updated:** December 9, 2025
**Setup Script Version:** 1.0.0
