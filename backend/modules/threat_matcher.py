"""
Threat Repetition & Pattern Recognition Module
Detects similar threats across incidents using multiple matching algorithms
"""

import sqlite3
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rakshanetra.db")

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings (0-1)"""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def extract_domain_from_text(text: str) -> Optional[str]:
    """Extract domain from URL in text"""
    url_pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
    match = re.search(url_pattern, text)
    if match:
        return match.group(1).lower()
    return None

def calculate_content_hash(content: str) -> str:
    """Generate hash of content for exact match detection"""
    normalized = re.sub(r'\s+', ' ', content.lower().strip())
    return hashlib.md5(normalized.encode()).hexdigest()

def extract_indicators(indicators_json: str) -> List[str]:
    """Extract indicators from JSON string"""
    try:
        if indicators_json:
            indicators = json.loads(indicators_json)
            if isinstance(indicators, list):
                return [str(i).lower() for i in indicators]
    except:
        pass
    return []

def calculate_indicator_overlap(indicators1: List[str], indicators2: List[str]) -> float:
    """Calculate overlap between two indicator lists (0-1)"""
    if not indicators1 or not indicators2:
        return 0.0
    
    set1 = set(indicators1)
    set2 = set(indicators2)
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0

def find_exact_matches(content: str, content_hash: str, conn) -> List[Dict]:
    """Find exact content matches"""
    cursor = conn.cursor()
    
    # Search by normalized content hash
    cursor.execute("""
        SELECT id, content, type, risk_score, severity, created_at, frequency_count
        FROM incidents
        WHERE content = ?
        ORDER BY created_at DESC
    """, (content,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row[0],
            'content': row[1],
            'type': row[2],
            'risk_score': row[3],
            'severity': row[4],
            'created_at': row[5],
            'frequency_count': row[6] or 1,
            'match_type': 'exact',
            'similarity': 1.0
        })
    
    return results

def find_domain_matches(content: str, incident_type: str, conn) -> List[Dict]:
    """Find incidents with same domain"""
    if incident_type not in ['url', 'email']:
        return []
    
    domain = extract_domain_from_text(content)
    if not domain:
        return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, type, risk_score, severity, created_at, frequency_count
        FROM incidents
        WHERE (type = 'url' OR type = 'email')
        AND content LIKE ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (f"%{domain}%",))
    
    results = []
    for row in cursor.fetchall():
        row_domain = extract_domain_from_text(row[1])
        if row_domain == domain:
            results.append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'risk_score': row[3],
                'severity': row[4],
                'created_at': row[5],
                'frequency_count': row[6] or 1,
                'match_type': 'domain',
                'similarity': 0.9,
                'matched_domain': domain
            })
    
    return results

def find_template_matches(content: str, incident_type: str, conn, threshold: float = 0.8) -> List[Dict]:
    """Find incidents with similar message templates"""
    if incident_type not in ['sms', 'email', 'message', 'social_media']:
        return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, type, risk_score, severity, created_at, frequency_count
        FROM incidents
        WHERE type IN ('sms', 'email', 'message', 'social_media')
        AND LENGTH(content) > 20
        ORDER BY created_at DESC
        LIMIT 100
    """)
    
    results = []
    for row in cursor.fetchall():
        similarity = calculate_text_similarity(content, row[1])
        
        if similarity >= threshold:
            results.append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'risk_score': row[3],
                'severity': row[4],
                'created_at': row[5],
                'frequency_count': row[6] or 1,
                'match_type': 'template',
                'similarity': round(similarity, 2)
            })
    
    return results

def find_indicator_matches(indicators: List[str], conn, threshold: int = 3) -> List[Dict]:
    """Find incidents with overlapping indicators"""
    if not indicators or len(indicators) < threshold:
        return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, content, type, risk_score, severity, created_at, frequency_count, indicators
        FROM incidents
        WHERE indicators IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 100
    """)
    
    results = []
    for row in cursor.fetchall():
        other_indicators = extract_indicators(row[7])
        overlap = calculate_indicator_overlap(indicators, other_indicators)
        
        # Check if at least 'threshold' indicators match
        common_count = len(set(indicators) & set(other_indicators))
        
        if common_count >= threshold or overlap >= 0.5:
            results.append({
                'id': row[0],
                'content': row[1],
                'type': row[2],
                'risk_score': row[3],
                'severity': row[4],
                'created_at': row[5],
                'frequency_count': row[6] or 1,
                'match_type': 'indicators',
                'similarity': round(overlap, 2),
                'common_indicators': common_count
            })
    
    return results

def find_similar_threats(
    content: str,
    content_type: str,
    indicators: List[str],
    exclude_id: Optional[str] = None
) -> Tuple[List[Dict], int, List[str]]:
    """
    Main function: Find all similar threats using multiple matching algorithms
    
    Returns:
        - List of similar incidents
        - Total frequency count
        - List of related incident IDs
    """
    conn = get_db()
    all_matches = {}
    
    try:
        content_hash = calculate_content_hash(content)
        
        # 1. Find exact matches
        exact_matches = find_exact_matches(content, content_hash, conn)
        for match in exact_matches:
            if exclude_id and match['id'] == exclude_id:
                continue
            all_matches[match['id']] = match
        
        # 2. Find domain matches (for URLs/emails)
        domain_matches = find_domain_matches(content, content_type, conn)
        for match in domain_matches:
            if exclude_id and match['id'] == exclude_id:
                continue
            if match['id'] not in all_matches:
                all_matches[match['id']] = match
        
        # 3. Find template matches (for messages)
        template_matches = find_template_matches(content, content_type, conn)
        for match in template_matches:
            if exclude_id and match['id'] == exclude_id:
                continue
            if match['id'] not in all_matches:
                all_matches[match['id']] = match
        
        # 4. Find indicator matches
        indicator_matches = find_indicator_matches(indicators, conn)
        for match in indicator_matches:
            if exclude_id and match['id'] == exclude_id:
                continue
            if match['id'] not in all_matches:
                all_matches[match['id']] = match
        
        # Convert to list and sort by similarity
        similar_incidents = sorted(
            all_matches.values(),
            key=lambda x: (x['similarity'], x['created_at']),
            reverse=True
        )
        
        # Calculate frequency count (including this incident)
        frequency_count = len(similar_incidents) + 1
        
        # Get related IDs
        related_ids = [match['id'] for match in similar_incidents]
        
        return similar_incidents, frequency_count, related_ids
        
    finally:
        conn.close()

def update_incident_frequency(incident_id: str, frequency_count: int, related_ids: List[str]):
    """Update incident with frequency data"""
    conn = get_db()
    try:
        related_ids_json = json.dumps(related_ids) if related_ids else None
        
        conn.execute("""
            UPDATE incidents
            SET frequency_count = ?,
                related_incident_ids = ?
            WHERE id = ?
        """, (frequency_count, related_ids_json, incident_id))
        
        conn.commit()
    finally:
        conn.close()

def get_similar_incidents(incident_id: str) -> List[Dict]:
    """Get all similar incidents for a given incident ID"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Get the incident
        cursor.execute("""
            SELECT content, type, indicators
            FROM incidents
            WHERE id = ?
        """, (incident_id,))
        
        row = cursor.fetchone()
        if not row:
            return []
        
        content, content_type, indicators_json = row
        indicators = extract_indicators(indicators_json)
        
        # Find similar threats
        similar, _, _ = find_similar_threats(content, content_type, indicators, exclude_id=incident_id)
        
        return similar
        
    finally:
        conn.close()

def get_recent_frequency_stats(days: int = 7) -> Dict:
    """Get frequency statistics for recent period"""
    conn = get_db()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_incidents,
                AVG(frequency_count) as avg_frequency,
                MAX(frequency_count) as max_frequency,
                SUM(CASE WHEN frequency_count > 5 THEN 1 ELSE 0 END) as high_frequency_count
            FROM incidents
            WHERE created_at >= ?
        """, (cutoff_date,))
        
        row = cursor.fetchone()
        
        return {
            'period_days': days,
            'total_incidents': row[0] or 0,
            'avg_frequency': round(row[1] or 0, 2),
            'max_frequency': row[2] or 0,
            'high_frequency_threats': row[3] or 0
        }
        
    finally:
        conn.close()
