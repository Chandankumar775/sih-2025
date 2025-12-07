"""
Incident Service - REAL SQLite Database Operations
No mock data - everything is stored and retrieved from local database!
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.core.database import (
    create_incident as db_create_incident,
    get_incident_by_id as db_get_incident,
    get_all_incidents as db_get_all_incidents,
    get_user_incidents as db_get_user_incidents,
    update_incident_status as db_update_status,
    get_incident_stats as db_get_stats
)
from app.models.schemas import (
    IncidentType, 
    SeverityLevel, 
    IncidentStatus,
    IncidentResponse,
    AnalysisResult
)


def generate_incident_id() -> str:
    """Generate a unique incident ID"""
    timestamp = datetime.now().strftime("%y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"INC-{timestamp}-{random_part}"


async def create_incident(
    incident_type: IncidentType,
    content: Optional[str],
    description: Optional[str],
    location: Optional[str],
    file_url: Optional[str],
    user_id: Optional[str],
    analysis: AnalysisResult
) -> Dict[str, Any]:
    """Create a new incident in SQLite database - REAL DATA!"""
    
    incident_id = generate_incident_id()
    
    # Prepare incident data for SQLite
    incident_data = {
        "type": incident_type.value,
        "content": content or "",
        "description": description,
        "location": location,
        "evidence_files": [file_url] if file_url else [],
        "reported_by": user_id,
        "risk_score": analysis.risk_score,
        "severity": analysis.severity.value,
        "status": IncidentStatus.PENDING.value,
        "indicators": analysis.indicators,
        "recommendations": analysis.recommendations,
    }
    
    # Save to SQLite database
    result = db_create_incident(incident_data)
    
    print(f"✅ REAL incident saved to database: {result['id']}")
    
    return {
        "success": True,
        "incident_id": incident_id,
        "db_id": result["id"],
        "analysis": analysis.model_dump()
    }


async def get_incidents(
    page: int = 1,
    per_page: int = 20,
    incident_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    user_id: Optional[str] = None,
    is_analyst: bool = False
) -> Dict[str, Any]:
    """Get paginated incidents from SQLite - REAL DATA!"""
    
    offset = (page - 1) * per_page
    
    # Get incidents from SQLite
    if user_id and not is_analyst:
        all_incidents = db_get_user_incidents(user_id, limit=1000)
    else:
        all_incidents = db_get_all_incidents(limit=1000, offset=0)
    
    # Apply filters
    filtered = all_incidents
    
    if incident_type and incident_type != "all":
        filtered = [i for i in filtered if i.get("type") == incident_type]
        
    if severity and severity != "all":
        filtered = [i for i in filtered if i.get("severity") == severity]
        
    if status and status != "all":
        filtered = [i for i in filtered if i.get("status") == status]
        
    if search:
        search_lower = search.lower()
        filtered = [i for i in filtered if 
                   search_lower in (i.get("content") or "").lower() or
                   search_lower in (i.get("description") or "").lower() or
                   search_lower in i.get("id", "").lower()]
    
    # Paginate
    total = len(filtered)
    paginated = filtered[offset:offset + per_page]
    
    # Format response
    incidents = []
    for row in paginated:
        incident = {
            "id": row["id"],
            "incident_id": row["id"][:18],  # Short ID for display
            "type": row["type"],
            "content": row.get("content"),
            "file_url": row.get("evidence_files", [None])[0] if row.get("evidence_files") else None,
            "description": row.get("description"),
            "location": row.get("location"),
            "risk_score": row.get("risk_score", 0),
            "severity": row.get("severity", "low"),
            "status": row.get("status", "pending"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
            "reported_by": row.get("reported_by") or "Anonymous Reporter",
            "indicators": row.get("indicators", []),
            "recommendations": row.get("recommendations", [])
        }
        incidents.append(incident)
    
    print(f"📊 Retrieved {len(incidents)} REAL incidents from database")
    
    return {
        "incidents": incidents,
        "total": total,
        "page": page,
        "per_page": per_page
    }


async def get_incident_by_id(incident_id: str) -> Optional[Dict[str, Any]]:
    """Get single incident from SQLite - REAL DATA!"""
    
    row = db_get_incident(incident_id)
    
    if not row:
        print(f"❌ Incident not found: {incident_id}")
        return None
    
    incident = {
        "id": row["id"],
        "incident_id": row["id"][:18],
        "type": row["type"],
        "content": row.get("content"),
        "file_url": row.get("evidence_files", [None])[0] if row.get("evidence_files") else None,
        "description": row.get("description"),
        "location": row.get("location"),
        "risk_score": row.get("risk_score", 0),
        "severity": row.get("severity", "low"),
        "status": row.get("status", "pending"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
    
    analysis = {
        "risk_score": row.get("risk_score", 0),
        "severity": row.get("severity", "low"),
        "summary": f"Analysis for {row['type']} incident",
        "indicators": row.get("indicators", []),
        "recommendations": row.get("recommendations", []),
        "iocs": [],
    }
    
    print(f"✅ Retrieved REAL incident: {incident_id}")
    
    return {
        "incident": incident,
        "analysis": analysis
    }


async def escalate_incident(incident_id: str, user_id: str) -> bool:
    """Escalate an incident to CERT - REAL UPDATE!"""
    
    success = db_update_status(incident_id, IncidentStatus.ESCALATED.value)
    
    if success:
        print(f"🚨 Incident {incident_id} ESCALATED in database")
    
    return success


async def update_incident_status(incident_id: str, status: IncidentStatus) -> bool:
    """Update incident status in SQLite - REAL UPDATE!"""
    
    success = db_update_status(incident_id, status.value)
    
    if success:
        print(f"✅ Incident {incident_id} status updated to {status.value}")
    
    return success


async def get_stats() -> Dict[str, Any]:
    """Get incident statistics from SQLite - REAL DATA!"""
    
    stats = db_get_stats()
    print(f"📈 Retrieved REAL stats: {stats['total_incidents']} total incidents")
    return stats
