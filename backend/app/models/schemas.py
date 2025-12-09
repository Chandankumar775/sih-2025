"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ================================
# ENUMS
# ================================

class IncidentType(str, Enum):
    URL = "url"
    MESSAGE = "message"
    FILE = "file"


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class UserRole(str, Enum):
    REPORTER = "reporter"
    ANALYST = "analyst"
    ADMIN = "admin"


# ================================
# AUTH MODELS
# ================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.REPORTER


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str


# ================================
# INCIDENT MODELS
# ================================

class IncidentCreate(BaseModel):
    type: IncidentType
    content: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    
    @validator('content')
    def content_required_for_url_message(cls, v, values):
        if values.get('type') in [IncidentType.URL, IncidentType.MESSAGE] and not v:
            raise ValueError('Content is required for URL and Message incidents')
        return v


class IncidentResponse(BaseModel):
    id: str
    incident_id: str;
    type: IncidentType
    content: Optional[str] = None
    file_url: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    risk_score: int = 0
    severity: SeverityLevel = SeverityLevel.LOW
    status: IncidentStatus = IncidentStatus.PENDING
    created_at: datetime
    updated_at: datetime
    reported_by: Optional[str] = None
    
    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    incidents: List[IncidentResponse]
    total: int
    page: int
    per_page: int


# ================================
# ANALYSIS MODELS
# ================================

class AnalysisResult(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    severity: SeverityLevel
    summary: str
    indicators: List[str]
    recommendations: List[str]
    iocs: Optional[List[str]] = []


class IncidentWithAnalysis(BaseModel):
    incident: IncidentResponse
    analysis: Optional[AnalysisResult] = None


class SubmitIncidentResponse(BaseModel):
    success: bool
    incident_id: str
    message: str
    analysis: AnalysisResult


# ================================
# ANALYTICS MODELS
# ================================

class TrendDataPoint(BaseModel):
    date: str
    count: int
    severity_breakdown: dict


class TrendsResponse(BaseModel):
    period: str
    data: List[TrendDataPoint]
    total_incidents: int


class RiskDistribution(BaseModel):
    critical: int
    high: int
    medium: int
    low: int


class StatsResponse(BaseModel):
    total_incidents: int
    pending_count: int
    critical_count: int
    analyzed_today: int
    average_risk_score: float
    risk_distribution: RiskDistribution


# ================================
# GENERAL MODELS
# ================================

class MessageResponse(BaseModel):
    success: bool
    message: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


# Update forward references
TokenResponse.model_rebuild()
