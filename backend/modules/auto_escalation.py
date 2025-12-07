"""
Auto-Escalation Engine Module
Automatically escalates threats based on risk score, frequency, and defence relevance
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rakshanetra.db")

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

# Escalation rules configuration
ESCALATION_RULES = {
    'critical_risk_score': 85,
    'high_frequency_threshold': 5,
    'frequency_check_days': 7,
    'defence_high_severity': True,
    'gov_impersonation': True
}

def should_escalate(incident_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Determine if an incident should be auto-escalated
    
    Args:
        incident_data: Dictionary with incident information
        
    Returns:
        (should_escalate, reason)
    """
    
    # Rule 1: Critical risk score (>= 85)
    if incident_data.get('risk_score', 0) >= ESCALATION_RULES['critical_risk_score']:
        return True, f"Critical risk score ({incident_data['risk_score']}/100)"
    
    # Rule 2: High frequency repetition (> 5 reports in 7 days)
    if incident_data.get('frequency_count', 1) > ESCALATION_RULES['high_frequency_threshold']:
        return True, f"Repeated threat ({incident_data['frequency_count']} reports in last {ESCALATION_RULES['frequency_check_days']} days)"
    
    # Rule 3: Army/Defence relevance + High severity
    if ESCALATION_RULES['defence_high_severity']:
        if incident_data.get('military_relevant') and incident_data.get('severity') in ['high', 'critical']:
            return True, "Defence-targeted high-severity threat"
    
    # Rule 4: Government domain impersonation
    if ESCALATION_RULES['gov_impersonation']:
        content = incident_data.get('content', '').lower()
        if ('gov.in' in content or 'nic.in' in content or 'government' in content) and incident_data.get('risk_score', 0) >= 60:
            return True, "Government domain impersonation detected"
    
    # Rule 5: Fake Army profile detected
    if incident_data.get('fake_profile_detected'):
        return True, "Fake Army profile/honeytrap detected"
    
    # Rule 6: Critical severity classification
    if incident_data.get('severity') == 'critical':
        return True, "Classified as CRITICAL severity"
    
    return False, None

def escalate_incident(incident_id: str, reason: str, auto: bool = True) -> bool:
    """
    Escalate an incident
    
    Args:
        incident_id: ID of incident to escalate
        reason: Reason for escalation
        auto: Whether this is auto-escalation (True) or manual (False)
        
    Returns:
        Success status
    """
    conn = get_db()
    try:
        timestamp = datetime.now().isoformat()
        
        conn.execute("""
            UPDATE incidents
            SET escalated_flag = 1,
                escalation_reason = ?,
                escalate_timestamp = ?,
                status = 'escalated'
            WHERE id = ?
        """, (reason, timestamp, incident_id))
        
        conn.commit()
        
        # Add to timeline
        add_to_timeline(
            incident_id,
            'escalated',
            f"{'Auto-escalated' if auto else 'Manually escalated'}: {reason}",
            'System' if auto else 'Officer'
        )
        
        return True
        
    except Exception as e:
        print(f"Error escalating incident {incident_id}: {e}")
        return False
    finally:
        conn.close()

def add_to_timeline(incident_id: str, event_type: str, description: str, performed_by: str):
    """Add event to incident timeline"""
    conn = get_db()
    try:
        import uuid
        timeline_id = f"TL-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().isoformat()
        
        conn.execute("""
            INSERT INTO incident_timeline (id, incident_id, event_type, event_description, performed_by, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (timeline_id, incident_id, event_type, description, performed_by, timestamp))
        
        conn.commit()
    finally:
        conn.close()

def check_and_escalate(incident_data: Dict, incident_id: str) -> Dict:
    """
    Check if incident should be escalated and do it
    
    Returns:
        Escalation info dict
    """
    should_escalate_flag, reason = should_escalate(incident_data)
    
    result = {
        'escalated': False,
        'reason': None,
        'auto': True
    }
    
    if should_escalate_flag:
        success = escalate_incident(incident_id, reason, auto=True)
        if success:
            result['escalated'] = True
            result['reason'] = reason
    
    return result

def get_escalated_incidents(limit: int = 50) -> List[Dict]:
    """Get all escalated incidents for CERT officer review"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, type, content, risk_score, severity, status,
                escalation_reason, escalate_timestamp, created_at,
                assigned_officer, geo_region, frequency_count
            FROM incidents
            WHERE escalated_flag = 1
            ORDER BY escalate_timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'type': row[1],
                'content': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                'risk_score': row[3],
                'severity': row[4],
                'status': row[5],
                'escalation_reason': row[6],
                'escalate_timestamp': row[7],
                'created_at': row[8],
                'assigned_officer': row[9],
                'geo_region': row[10],
                'frequency_count': row[11] or 1
            })
        
        return results
        
    finally:
        conn.close()

def manual_escalate(incident_id: str, reason: str, officer_name: str = "Officer") -> bool:
    """Manually escalate an incident"""
    return escalate_incident(incident_id, f"Manual escalation by {officer_name}: {reason}", auto=False)

def de_escalate(incident_id: str, reason: str) -> bool:
    """Remove escalation from incident"""
    conn = get_db()
    try:
        conn.execute("""
            UPDATE incidents
            SET escalated_flag = 0,
                escalation_reason = NULL,
                escalate_timestamp = NULL,
                status = 'investigating'
            WHERE id = ?
        """, (incident_id,))
        
        conn.commit()
        
        add_to_timeline(incident_id, 'de-escalated', f"De-escalated: {reason}", 'Officer')
        
        return True
        
    except Exception as e:
        print(f"Error de-escalating incident {incident_id}: {e}")
        return False
    finally:
        conn.close()

def get_escalation_stats(days: int = 7) -> Dict:
    """Get escalation statistics"""
    conn = get_db()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.cursor()
        
        # Total escalated
        cursor.execute("""
            SELECT COUNT(*) FROM incidents
            WHERE escalated_flag = 1
            AND escalate_timestamp >= ?
        """, (cutoff_date,))
        total_escalated = cursor.fetchone()[0]
        
        # By reason
        cursor.execute("""
            SELECT escalation_reason, COUNT(*) as count
            FROM incidents
            WHERE escalated_flag = 1
            AND escalate_timestamp >= ?
            GROUP BY escalation_reason
            ORDER BY count DESC
        """, (cutoff_date,))
        
        by_reason = [{'reason': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Pending escalated (not resolved)
        cursor.execute("""
            SELECT COUNT(*) FROM incidents
            WHERE escalated_flag = 1
            AND status != 'resolved'
        """)
        pending_escalated = cursor.fetchone()[0]
        
        return {
            'period_days': days,
            'total_escalated': total_escalated,
            'pending_review': pending_escalated,
            'by_reason': by_reason
        }
        
    finally:
        conn.close()

def update_escalation_rules(new_rules: Dict) -> bool:
    """Update escalation rules configuration"""
    global ESCALATION_RULES
    try:
        ESCALATION_RULES.update(new_rules)
        return True
    except Exception as e:
        print(f"Error updating escalation rules: {e}")
        return False

def get_escalation_rules() -> Dict:
    """Get current escalation rules"""
    return ESCALATION_RULES.copy()
