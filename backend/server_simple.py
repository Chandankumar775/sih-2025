"""
RakshaNetra Backend Server - SIMPLIFIED VERSION
No AI/NLP - Just Simple Mock Analysis
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import uuid
import os
import json
from datetime import datetime
import random

# Import authentication manager only
from modules.auth_manager import auth_manager

app = FastAPI(title="RakshaNetra API - Simple", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "rakshanetra_simple.db")

# ==================== DATABASE ====================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT,
            file_name TEXT,
            unit TEXT,
            location TEXT,
            notes TEXT,
            risk_score INTEGER DEFAULT 0,
            severity TEXT DEFAULT 'low',
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            reporter_id TEXT,
            reporter_username TEXT,
            mock_analysis TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[OK] Database ready at: {DB_PATH}")

# Initialize on startup
init_db()

# ==================== MOCK ANALYSIS GENERATOR ====================
def generate_mock_analysis(incident_type: str, content: str) -> dict:
    """Generate simple mock analysis - NO AI/NLP"""
    
    # Simple risk scoring based on keywords
    risk_keywords = ['urgent', 'click here', 'verify', 'account', 'suspended', 'prize', 'winner', 'claim']
    risk_score = 30  # base score
    
    content_lower = content.lower() if content else ""
    for keyword in risk_keywords:
        if keyword in content_lower:
            risk_score += 10
    
    risk_score = min(risk_score, 95)
    
    # Determine severity
    if risk_score >= 80:
        severity = "critical"
    elif risk_score >= 60:
        severity = "high"
    elif risk_score >= 40:
        severity = "medium"
    else:
        severity = "low"
    
    # Mock threat types based on incident type
    threat_types = {
        "url": "Phishing URL",
        "sms": "SMS Scam (Smishing)",
        "email": "Email Phishing",
        "call": "Voice Phishing (Vishing)",
        "file": "Suspicious File",
        "other": "Suspicious Activity"
    }
    
    threat_type = threat_types.get(incident_type, "Unknown Threat")
    
    return {
        "risk_score": risk_score,
        "severity": severity,
        "threat_type": threat_type,
        "summary": f"Potential {threat_type} detected - Risk: {severity.upper()}",
        "indicators": [
            "Suspicious pattern detected",
            "Potential social engineering attempt",
            "Requires security review"
        ],
        "recommendations": [
            "Do not click any links",
            "Do not share sensitive information",
            "Report to CERT team immediately",
            "Monitor for similar attempts"
        ],
        "analysis_timestamp": datetime.now().isoformat(),
        "analyst_notes": []
    }

# ==================== MODELS ====================
class IncidentCreate(BaseModel):
    type: str
    content: Optional[str] = None
    file_name: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str = "reporter"

# ==================== HEALTH CHECK ====================
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "RakshaNetra Simple Backend"}

# ==================== AUTH ENDPOINTS ====================
@app.post("/api/auth/register")
def register(request: RegisterRequest):
    try:
        result = auth_manager.register_user(
            username=request.username,
            password=request.password,
            email=request.email,
            role=request.role
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
def login(request: LoginRequest):
    try:
        result = auth_manager.login_user(request.username, request.password)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    token = authorization.replace("Bearer ", "")
    try:
        auth_manager.logout_user(token)
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/auth/verify")
def verify_token(token: str):
    try:
        payload = auth_manager.verify_token(token)
        return {"valid": True, "user": payload}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== INCIDENT ENDPOINTS ====================
@app.post("/api/incidents/report")
def report_incident(incident: IncidentCreate, authorization: Optional[str] = Header(None)):
    """Simple incident report - generates mock analysis"""
    
    # Get user info if authenticated
    reporter_id = "anonymous"
    reporter_username = "anonymous"
    
    if authorization:
        token = authorization.replace("Bearer ", "")
        try:
            payload = auth_manager.verify_token(token)
            reporter_id = payload.get("user_id", "anonymous")
            reporter_username = payload.get("username", "anonymous")
        except:
            pass
    
    # Generate incident ID
    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    
    # Generate mock analysis
    mock_analysis = generate_mock_analysis(incident.type, incident.content or "")
    
    # Store in database
    conn = get_db()
    conn.execute("""
        INSERT INTO incidents (
            id, type, content, file_name, unit, location, notes,
            risk_score, severity, status, created_at, reporter_id, 
            reporter_username, mock_analysis
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_id,
        incident.type,
        incident.content,
        incident.file_name,
        incident.unit,
        incident.location,
        incident.notes,
        mock_analysis["risk_score"],
        mock_analysis["severity"],
        "pending",
        datetime.now().isoformat(),
        reporter_id,
        reporter_username,
        json.dumps(mock_analysis)
    ))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Incident {incident_id} created by {reporter_username}")
    
    # Return minimal response for reporters
    return {
        "success": True,
        "incident_id": incident_id,
        "submitted_at": datetime.now().isoformat(),
        "message": "Report submitted successfully"
    }

@app.get("/api/incidents")
def get_incidents(authorization: Optional[str] = Header(None)):
    """Get all incidents - admin only"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = auth_manager.verify_token(token)
        role = payload.get("role")
        
        if role not in ["admin", "analyst"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        conn = get_db()
        cursor = conn.execute("""
            SELECT * FROM incidents ORDER BY created_at DESC
        """)
        incidents = []
        for row in cursor.fetchall():
            incident = dict(row)
            # Parse mock analysis
            if incident["mock_analysis"]:
                try:
                    incident["analysis"] = json.loads(incident["mock_analysis"])
                except:
                    incident["analysis"] = {}
            incidents.append(incident)
        conn.close()
        
        return {"success": True, "incidents": incidents}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str, authorization: Optional[str] = Header(None)):
    """Get single incident details"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = auth_manager.verify_token(token)
        
        conn = get_db()
        cursor = conn.execute("""
            SELECT * FROM incidents WHERE id = ?
        """, (incident_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = dict(row)
        if incident["mock_analysis"]:
            try:
                incident["analysis"] = json.loads(incident["mock_analysis"])
            except:
                incident["analysis"] = {}
        
        return {"success": True, "incident": incident}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.put("/api/incidents/{incident_id}/status")
def update_status(incident_id: str, status: str, authorization: Optional[str] = Header(None)):
    """Update incident status - admin only"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = auth_manager.verify_token(token)
        role = payload.get("role")
        
        if role not in ["admin", "analyst"]:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        conn = get_db()
        conn.execute("""
            UPDATE incidents SET status = ? WHERE id = ?
        """, (status, incident_id))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Status updated to {status}"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== RUN SERVER ====================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🛡️  RAKSHANETRA SIMPLE API SERVER")
    print("="*50)
    print(f"📁 Database: {DB_PATH}")
    print("🌐 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
