"""
Analytics Routes
Handles trends, statistics, and reporting
"""

from fastapi import APIRouter, Depends
from app.core.security import get_analyst_or_admin
from app.models.schemas import TrendsResponse, StatsResponse, RiskDistribution
from app.services.analytics_service import (
    get_incident_stats,
    get_trends,
    get_risk_distribution
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(current_user: dict = Depends(get_analyst_or_admin)):
    """
    Get incident statistics (Analysts/Admins only)
    """
    stats = await get_incident_stats()
    return StatsResponse(**stats)


@router.get("/trends", response_model=TrendsResponse)
async def get_incident_trends(
    period: str = "7d",
    current_user: dict = Depends(get_analyst_or_admin)
):
    """
    Get incident trends over time
    
    - **period**: 7d, 30d, or 90d
    """
    if period not in ["7d", "30d", "90d"]:
        period = "7d"
    
    trends = await get_trends(period)
    return TrendsResponse(**trends)


@router.get("/risk-distribution", response_model=RiskDistribution)
async def get_risk_dist(current_user: dict = Depends(get_analyst_or_admin)):
    """
    Get distribution of incidents by severity
    """
    distribution = await get_risk_distribution()
    return RiskDistribution(**distribution)
