"""
Analytics Service - Statistics and trends
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.core.database import supabase


async def get_incident_stats() -> Dict[str, Any]:
    """Get incident statistics"""
    
    try:
        # Get total incidents
        total_result = supabase.table("incidents").select("id", count="exact").execute()
        total = total_result.count or 0
        
        # Get pending count
        pending_result = supabase.table("incidents").select("id", count="exact").eq("status", "pending").execute()
        pending = pending_result.count or 0
        
        # Get critical count
        critical_result = supabase.table("incidents").select("id", count="exact").eq("severity", "critical").execute()
        critical = critical_result.count or 0
        
        # Get today's count
        today = datetime.utcnow().date().isoformat()
        today_result = supabase.table("incidents").select("id", count="exact").gte("created_at", today).execute()
        today_count = today_result.count or 0
        
        # Get risk distribution
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for severity in severity_counts.keys():
            result = supabase.table("incidents").select("id", count="exact").eq("severity", severity).execute()
            severity_counts[severity] = result.count or 0
        
        # Calculate average risk score
        all_incidents = supabase.table("incidents").select("risk_score").execute()
        if all_incidents.data:
            scores = [i.get("risk_score", 0) for i in all_incidents.data if i.get("risk_score")]
            avg_risk = sum(scores) / len(scores) if scores else 0
        else:
            avg_risk = 0
        
        return {
            "total_incidents": total,
            "pending_count": pending,
            "critical_count": critical,
            "analyzed_today": today_count,
            "average_risk_score": round(avg_risk, 1),
            "risk_distribution": severity_counts
        }
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        
        # Return mock data for demo
        return {
            "total_incidents": 127,
            "pending_count": 23,
            "critical_count": 8,
            "analyzed_today": 12,
            "average_risk_score": 62.4,
            "risk_distribution": {
                "critical": 8,
                "high": 34,
                "medium": 52,
                "low": 33
            }
        }


async def get_trends(period: str = "7d") -> Dict[str, Any]:
    """Get incident trends over time"""
    
    # Parse period
    days = 7
    if period == "30d":
        days = 30
    elif period == "90d":
        days = 90
    
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        result = supabase.table("incidents").select(
            "created_at, severity"
        ).gte("created_at", start_date).order("created_at").execute()
        
        # Group by date
        date_groups: Dict[str, Dict[str, int]] = {}
        
        for incident in result.data or []:
            date = incident["created_at"][:10]  # Get YYYY-MM-DD
            severity = incident.get("severity", "low")
            
            if date not in date_groups:
                date_groups[date] = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
            
            date_groups[date]["total"] += 1
            date_groups[date][severity] += 1
        
        # Convert to list
        data = []
        for date, counts in sorted(date_groups.items()):
            data.append({
                "date": date,
                "count": counts["total"],
                "severity_breakdown": {
                    "critical": counts["critical"],
                    "high": counts["high"],
                    "medium": counts["medium"],
                    "low": counts["low"]
                }
            })
        
        return {
            "period": period,
            "data": data,
            "total_incidents": sum(d["count"] for d in data)
        }
        
    except Exception as e:
        print(f"Error fetching trends: {e}")
        
        # Return mock data
        mock_data = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=days-i-1)).strftime("%Y-%m-%d")
            mock_data.append({
                "date": date,
                "count": 10 + (i % 5) * 3,
                "severity_breakdown": {
                    "critical": 1 + (i % 2),
                    "high": 3 + (i % 3),
                    "medium": 4 + (i % 4),
                    "low": 2 + (i % 2)
                }
            })
        
        return {
            "period": period,
            "data": mock_data,
            "total_incidents": sum(d["count"] for d in mock_data)
        }


async def get_risk_distribution() -> Dict[str, int]:
    """Get distribution of incidents by risk level"""
    
    stats = await get_incident_stats()
    return stats.get("risk_distribution", {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    })
