# 🚀 RakshaNetra - Quick Start Guide

## ✅ Recommended: Auto-Restart Mode (Always Running)

**Double-click: `START.bat`** then **`KEEP_ALIVE.bat`**

This will:
1. Start both servers (Backend + Frontend)
2. Monitor them every 10 seconds
3. Auto-restart if either crashes
4. Keep running even if you accidentally close terminals

**Benefits:**
- ✅ Servers never go down
- ✅ Auto-recovery from crashes
- ✅ Perfect for demos/presentations
- ✅ No manual restarts needed

**To Stop:**
- Close the "RakshaNetra - Auto Restart Monitor" window
- Or double-click `STOP.bat`

---

## 🔧 Manual Start (One-time)

**Double-click: `START.bat`**

This will:
1. Start backend on port 8000
2. Start frontend on port 8080
3. Open browser automatically

**Note:** Servers will stop if you close the terminal windows.

---

## 🛑 Stop All Servers

**Double-click: `STOP.bat`**

This will kill all processes on ports 8000 and 8080.

---

## 📍 URLs

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Problem: "Site can't be reached"
**Solution:** Run `START.bat` or `KEEP_ALIVE.bat`

### Problem: Servers keep stopping
**Solution:** Use `KEEP_ALIVE.bat` for auto-restart

### Problem: Port already in use
**Solution:** Run `STOP.bat` first, then `START.bat`

---

## 📂 Batch Files Explained

| File | Purpose |
|------|---------|
| `START.bat` | One-time start (servers stop if terminals close) |
| `KEEP_ALIVE.bat` | Auto-restart monitor (servers never stop) |
| `STOP.bat` | Kill all servers |

---

**For SIH 2025 Demo:** Use `START.bat` + `KEEP_ALIVE.bat` for 100% uptime! 🎯
