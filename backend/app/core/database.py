"""
SQLite Database - Local database for SIH project
No external dependencies needed!
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import uuid

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "rakshanetra.db")


def get_db_connection() -> sqlite3.Connection:
    """Get SQLite database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_database():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'citizen',
            phone TEXT,
            organization TEXT,
            department TEXT,
            is_verified INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            description TEXT,
            risk_score INTEGER DEFAULT 0,
            severity TEXT DEFAULT 'unknown',
            status TEXT DEFAULT 'pending',
            indicators TEXT,
            recommendations TEXT,
            evidence_files TEXT,
            reported_by TEXT,
            assigned_to TEXT,
            location TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT
        )
    """)
    
    # Analytics/Stats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            total_incidents INTEGER DEFAULT 0,
            high_severity INTEGER DEFAULT 0,
            medium_severity INTEGER DEFAULT 0,
            low_severity INTEGER DEFAULT 0,
            resolved INTEGER DEFAULT 0,
            pending INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")


# ============== USER OPERATIONS ==============

def create_user(email: str, password_hash: str, full_name: str = None, role: str = "citizen") -> Dict[str, Any]:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO users (id, email, password_hash, full_name, role, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, email, password_hash, full_name, role, now, now))
    
    conn.commit()
    conn.close()
    
    return {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


# ============== INCIDENT OPERATIONS ==============

def create_incident(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new incident"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    incident_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Convert lists to JSON strings
    indicators = json.dumps(incident_data.get("indicators", []))
    recommendations = json.dumps(incident_data.get("recommendations", []))
    evidence_files = json.dumps(incident_data.get("evidence_files", []))
    
    cursor.execute("""
        INSERT INTO incidents (
            id, type, content, description, risk_score, severity, status,
            indicators, recommendations, evidence_files, reported_by,
            location, ip_address, user_agent, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_id,
        incident_data.get("type"),
        incident_data.get("content"),
        incident_data.get("description"),
        incident_data.get("risk_score", 0),
        incident_data.get("severity", "unknown"),
        incident_data.get("status", "pending"),
        indicators,
        recommendations,
        evidence_files,
        incident_data.get("reported_by"),
        incident_data.get("location"),
        incident_data.get("ip_address"),
        incident_data.get("user_agent"),
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "id": incident_id,
        **incident_data,
        "created_at": now,
        "updated_at": now
    }


def get_incident_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get incident by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        incident = dict(row)
        # Parse JSON fields
        incident["indicators"] = json.loads(incident.get("indicators") or "[]")
        incident["recommendations"] = json.loads(incident.get("recommendations") or "[]")
        incident["evidence_files"] = json.loads(incident.get("evidence_files") or "[]")
        return incident
    return None


def get_all_incidents(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Get all incidents with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM incidents 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    incidents = []
    for row in rows:
        incident = dict(row)
        incident["indicators"] = json.loads(incident.get("indicators") or "[]")
        incident["recommendations"] = json.loads(incident.get("recommendations") or "[]")
        incident["evidence_files"] = json.loads(incident.get("evidence_files") or "[]")
        incidents.append(incident)
    
    return incidents


def get_user_incidents(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get incidents reported by a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM incidents 
        WHERE reported_by = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    incidents = []
    for row in rows:
        incident = dict(row)
        incident["indicators"] = json.loads(incident.get("indicators") or "[]")
        incident["recommendations"] = json.loads(incident.get("recommendations") or "[]")
        incident["evidence_files"] = json.loads(incident.get("evidence_files") or "[]")
        incidents.append(incident)
    
    return incidents


def update_incident_status(incident_id: str, status: str) -> bool:
    """Update incident status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    resolved_at = now if status == "resolved" else None
    
    cursor.execute("""
        UPDATE incidents 
        SET status = ?, updated_at = ?, resolved_at = ?
        WHERE id = ?
    """, (status, now, resolved_at, incident_id))
    
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0


def get_incident_stats() -> Dict[str, Any]:
    """Get incident statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total incidents
    cursor.execute("SELECT COUNT(*) FROM incidents")
    total = cursor.fetchone()[0]
    
    # By severity
    cursor.execute("SELECT severity, COUNT(*) FROM incidents GROUP BY severity")
    by_severity = {row[0]: row[1] for row in cursor.fetchall()}
    
    # By status
    cursor.execute("SELECT status, COUNT(*) FROM incidents GROUP BY status")
    by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    # By type
    cursor.execute("SELECT type, COUNT(*) FROM incidents GROUP BY type")
    by_type = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Recent 7 days
    cursor.execute("""
        SELECT DATE(created_at), COUNT(*) 
        FROM incidents 
        WHERE created_at >= DATE('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY DATE(created_at)
    """)
    recent_trend = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_incidents": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "by_type": by_type,
        "recent_trend": recent_trend,
        "high_severity_count": by_severity.get("high", 0) + by_severity.get("critical", 0),
        "pending_count": by_status.get("pending", 0),
        "resolved_count": by_status.get("resolved", 0)
    }


# Initialize database on module load
init_database()
