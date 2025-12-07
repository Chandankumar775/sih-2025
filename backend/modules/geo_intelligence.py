"""
Geo-Intelligence Module
Maps incidents to Indian Defence Command regions and provides geographic analysis
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rakshanetra.db")

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

# Indian Defence Command regions mapping
DEFENCE_COMMAND_REGIONS = {
    'Northern Command': {
        'states': ['Jammu & Kashmir', 'Jammu and Kashmir', 'Ladakh', 'Himachal Pradesh', 'Punjab', 'Chandigarh'],
        'abbrev': ['J&K', 'JK', 'HP', 'PB', 'CHD'],
        'headquarters': 'Udhampur',
        'priority': 'critical'
    },
    'Western Command': {
        'states': ['Rajasthan', 'Gujarat', 'parts of Maharashtra'],
        'abbrev': ['RJ', 'GJ', 'MH'],
        'headquarters': 'Chandimandir',
        'priority': 'high'
    },
    'Eastern Command': {
        'states': ['West Bengal', 'Bihar', 'Jharkhand', 'Sikkim', 'Assam', 'Arunachal Pradesh', 
                   'Nagaland', 'Manipur', 'Mizoram', 'Tripura', 'Meghalaya'],
        'abbrev': ['WB', 'BH', 'JH', 'SK', 'AS', 'AR', 'NL', 'MN', 'MZ', 'TR', 'ML'],
        'headquarters': 'Kolkata',
        'priority': 'critical'
    },
    'Southern Command': {
        'states': ['Karnataka', 'Kerala', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 
                   'Andaman & Nicobar', 'Lakshadweep'],
        'abbrev': ['KA', 'KL', 'TN', 'AP', 'TS', 'AN'],
        'headquarters': 'Pune',
        'priority': 'medium'
    },
    'South Western Command': {
        'states': ['Maharashtra', 'Madhya Pradesh', 'Chhattisgarh', 'Goa'],
        'abbrev': ['MH', 'MP', 'CG', 'GA'],
        'headquarters': 'Jaipur',
        'priority': 'medium'
    },
    'Central Command': {
        'states': ['Uttar Pradesh', 'Uttarakhand'],
        'abbrev': ['UP', 'UK', 'UH'],
        'headquarters': 'Lucknow',
        'priority': 'high'
    },
    'Delhi Area': {
        'states': ['Delhi', 'NCR', 'National Capital Region'],
        'abbrev': ['DL', 'NCR'],
        'headquarters': 'Delhi',
        'priority': 'critical'
    }
}

# City to state mapping (major cities)
CITY_TO_STATE = {
    'Mumbai': 'Maharashtra', 'Delhi': 'Delhi', 'Bangalore': 'Karnataka', 'Bengaluru': 'Karnataka',
    'Hyderabad': 'Telangana', 'Chennai': 'Tamil Nadu', 'Kolkata': 'West Bengal',
    'Pune': 'Maharashtra', 'Ahmedabad': 'Gujarat', 'Jaipur': 'Rajasthan',
    'Surat': 'Gujarat', 'Lucknow': 'Uttar Pradesh', 'Kanpur': 'Uttar Pradesh',
    'Nagpur': 'Maharashtra', 'Indore': 'Madhya Pradesh', 'Thane': 'Maharashtra',
    'Bhopal': 'Madhya Pradesh', 'Visakhapatnam': 'Andhra Pradesh', 'Pimpri-Chinchwad': 'Maharashtra',
    'Patna': 'Bihar', 'Vadodara': 'Gujarat', 'Ghaziabad': 'Uttar Pradesh',
    'Ludhiana': 'Punjab', 'Agra': 'Uttar Pradesh', 'Nashik': 'Maharashtra',
    'Faridabad': 'Haryana', 'Meerut': 'Uttar Pradesh', 'Rajkot': 'Gujarat',
    'Varanasi': 'Uttar Pradesh', 'Srinagar': 'Jammu & Kashmir', 'Amritsar': 'Punjab',
    'Chandigarh': 'Chandigarh', 'Guwahati': 'Assam', 'Imphal': 'Manipur',
    'Shimla': 'Himachal Pradesh', 'Ranchi': 'Jharkhand', 'Bhubaneswar': 'Odisha'
}

def extract_location_from_text(text: str) -> Optional[str]:
    """Try to extract location (state/city) from text"""
    text_lower = text.lower()
    
    # Check for Indian states and UTs
    indian_states = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
        'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
        'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
        'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
        'Andaman and Nicobar', 'Chandigarh', 'Dadra and Nagar Haveli', 'Daman and Diu',
        'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
    ]
    
    for state in indian_states:
        if state.lower() in text_lower:
            return state
    
    # Check for major cities
    for city, state in CITY_TO_STATE.items():
        if city.lower() in text_lower:
            return state
    
    return None

def map_location_to_command(location: str) -> str:
    """Map a location (state/city) to its Defence Command"""
    if not location:
        return 'Unknown Region'
    
    location_lower = location.lower()
    
    # First, resolve city to state if it's a city
    if location in CITY_TO_STATE:
        location = CITY_TO_STATE[location]
        location_lower = location.lower()
    
    # Check each command's states
    for command, data in DEFENCE_COMMAND_REGIONS.items():
        for state in data['states']:
            if state.lower() in location_lower or location_lower in state.lower():
                return command
        
        # Check abbreviations
        for abbrev in data['abbrev']:
            if abbrev.lower() == location_lower:
                return command
    
    return 'Unknown Region'

def update_incident_geo_region(incident_id: str, geo_region: str):
    """Update incident with geo region"""
    conn = get_db()
    try:
        conn.execute("""
            UPDATE incidents
            SET geo_region = ?
            WHERE id = ?
        """, (geo_region, incident_id))
        conn.commit()
    finally:
        conn.close()

def update_geo_statistics(region: str, severity: str, escalated: bool):
    """Update geo statistics table"""
    conn = get_db()
    try:
        import uuid
        date_today = datetime.now().date().isoformat()
        
        # Check if record exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, incident_count, high_severity_count, escalated_count
            FROM geo_statistics
            WHERE region = ? AND date = ?
        """, (region, date_today))
        
        row = cursor.fetchone()
        
        if row:
            # Update existing record
            stat_id, incident_count, high_severity_count, escalated_count = row
            
            new_incident_count = incident_count + 1
            new_high_severity = high_severity_count + (1 if severity in ['high', 'critical'] else 0)
            new_escalated = escalated_count + (1 if escalated else 0)
            
            conn.execute("""
                UPDATE geo_statistics
                SET incident_count = ?,
                    high_severity_count = ?,
                    escalated_count = ?,
                    updated_at = ?
                WHERE id = ?
            """, (new_incident_count, new_high_severity, new_escalated, 
                  datetime.now().isoformat(), stat_id))
        else:
            # Create new record
            stat_id = f"GEO-{uuid.uuid4().hex[:8].upper()}"
            conn.execute("""
                INSERT INTO geo_statistics 
                (id, region, date, incident_count, high_severity_count, escalated_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stat_id, region, date_today, 1,
                  1 if severity in ['high', 'critical'] else 0,
                  1 if escalated else 0,
                  datetime.now().isoformat()))
        
        conn.commit()
    finally:
        conn.close()

def get_geo_heatmap(days: int = 7) -> Dict:
    """Get incident count by defence command for heatmap visualization"""
    conn = get_db()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                geo_region,
                COUNT(*) as total,
                SUM(CASE WHEN severity IN ('high', 'critical') THEN 1 ELSE 0 END) as high_severity,
                SUM(CASE WHEN escalated_flag = 1 THEN 1 ELSE 0 END) as escalated,
                AVG(risk_score) as avg_risk
            FROM incidents
            WHERE created_at >= ?
            AND geo_region IS NOT NULL
            AND geo_region != 'Unknown Region'
            GROUP BY geo_region
            ORDER BY total DESC
        """, (cutoff_date,))
        
        heatmap_data = {}
        for row in cursor.fetchall():
            region, total, high_sev, escalated, avg_risk = row
            
            command_info = DEFENCE_COMMAND_REGIONS.get(region, {})
            
            heatmap_data[region] = {
                'total_incidents': total,
                'high_severity_count': high_sev,
                'escalated_count': escalated,
                'avg_risk_score': round(avg_risk, 1) if avg_risk else 0,
                'priority': command_info.get('priority', 'medium'),
                'headquarters': command_info.get('headquarters', 'N/A')
            }
        
        return {
            'period_days': days,
            'commands': heatmap_data,
            'total_commands_affected': len(heatmap_data)
        }
        
    finally:
        conn.close()

def get_geo_trends(days: int = 30) -> Dict:
    """Get geographic trends over time"""
    conn = get_db()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT region, date, incident_count, high_severity_count, escalated_count
            FROM geo_statistics
            WHERE date >= ?
            ORDER BY date DESC, incident_count DESC
        """, (cutoff_date,))
        
        trends_by_region = defaultdict(list)
        
        for row in cursor.fetchall():
            region, date, inc_count, high_sev, escalated = row
            trends_by_region[region].append({
                'date': date,
                'incidents': inc_count,
                'high_severity': high_sev,
                'escalated': escalated
            })
        
        return {
            'period_days': days,
            'trends': dict(trends_by_region)
        }
        
    finally:
        conn.close()

def get_hotspot_regions(threshold: int = 10, days: int = 7) -> List[Dict]:
    """Identify hotspot regions with high incident concentration"""
    conn = get_db()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                geo_region,
                COUNT(*) as total,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count,
                SUM(CASE WHEN escalated_flag = 1 THEN 1 ELSE 0 END) as escalated_count
            FROM incidents
            WHERE created_at >= ?
            AND geo_region IS NOT NULL
            AND geo_region != 'Unknown Region'
            GROUP BY geo_region
            HAVING total >= ?
            ORDER BY total DESC
        """, (cutoff_date, threshold))
        
        hotspots = []
        for row in cursor.fetchall():
            region, total, critical, escalated = row
            
            command_info = DEFENCE_COMMAND_REGIONS.get(region, {})
            
            hotspots.append({
                'region': region,
                'total_incidents': total,
                'critical_incidents': critical,
                'escalated_incidents': escalated,
                'priority': command_info.get('priority', 'medium'),
                'alert_level': 'high' if total >= threshold * 2 else 'medium'
            })
        
        return hotspots
        
    finally:
        conn.close()

def get_region_details(region: str, days: int = 30) -> Dict:
    """Get detailed statistics for a specific region"""
    conn = get_db()
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(risk_score) as avg_risk,
                SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN escalated_flag = 1 THEN 1 ELSE 0 END) as escalated,
                SUM(CASE WHEN military_relevant = 1 THEN 1 ELSE 0 END) as defence_targeted
            FROM incidents
            WHERE geo_region = ?
            AND created_at >= ?
        """, (region, cutoff_date))
        
        row = cursor.fetchone()
        
        # Get incident types breakdown
        cursor.execute("""
            SELECT type, COUNT(*) as count
            FROM incidents
            WHERE geo_region = ?
            AND created_at >= ?
            GROUP BY type
            ORDER BY count DESC
        """, (region, cutoff_date))
        
        types_breakdown = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        command_info = DEFENCE_COMMAND_REGIONS.get(region, {})
        
        return {
            'region': region,
            'command_info': command_info,
            'period_days': days,
            'total_incidents': row[0] or 0,
            'avg_risk_score': round(row[1], 1) if row[1] else 0,
            'severity_breakdown': {
                'low': row[2] or 0,
                'medium': row[3] or 0,
                'high': row[4] or 0,
                'critical': row[5] or 0
            },
            'escalated_incidents': row[6] or 0,
            'defence_targeted': row[7] or 0,
            'incident_types': types_breakdown
        }
        
    finally:
        conn.close()

def get_all_commands_info() -> Dict:
    """Get information about all defence commands"""
    return {
        'commands': DEFENCE_COMMAND_REGIONS,
        'total_commands': len(DEFENCE_COMMAND_REGIONS)
    }
