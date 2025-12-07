"""
Incident Routes
Handles incident submission, retrieval, and management
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Optional
from app.core.security import get_current_user, get_analyst_or_admin, get_current_user_optional
from app.models.schemas import (
    IncidentType,
    IncidentCreate,
    IncidentResponse,
    IncidentListResponse,
    IncidentWithAnalysis,
    SubmitIncidentResponse,
    MessageResponse,
    AnalysisResult
)
from app.services.ai_analyzer import analyze_threat
from app.services.incident_service import (
    create_incident,
    get_incidents,
    get_incident_by_id,
    escalate_incident
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=SubmitIncidentResponse)
async def submit_incident(
    type: IncidentType = Form(...),
    content: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user_optional)
):
    """
    Submit a new incident for AI analysis
    
    - **type**: url, message, or file
    - **content**: The suspicious content (required for url/message)
    - **description**: Additional context
    - **location**: Unit/location of reporter
    - **file**: Suspicious file upload (for file type)
    """
    
    # Validate content based on type
    if type in [IncidentType.URL, IncidentType.MESSAGE] and not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content is required for {type.value} incidents"
        )
    
    if type == IncidentType.FILE and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is required for file incidents"
        )
    
    # Handle file upload
    file_url = None
    file_info = None
    analysis_content = content or ""
    
    if file:
        # Read file content for analysis
        file_content = await file.read()
        file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(file_content)
        }
        analysis_content = f"File: {file.filename} (Type: {file.content_type}, Size: {len(file_content)} bytes)"
        
        # TODO: Upload to storage and get URL
        file_url = f"uploads/{file.filename}"
    
    # Perform AI analysis
    analysis = await analyze_threat(
        incident_type=type,
        content=analysis_content,
        description=description,
        file_info=file_info
    )
    
    # Store incident
    result = await create_incident(
        incident_type=type,
        content=content,
        description=description,
        location=location,
        file_url=file_url,
        user_id=current_user.get("id"),
        analysis=analysis
    )
    
    return SubmitIncidentResponse(
        success=True,
        incident_id=result["incident_id"],
        message="Incident submitted and analyzed successfully",
        analysis=analysis
    )


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    page: int = 1,
    per_page: int = 20,
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get paginated list of incidents
    
    - Analysts/Admins see all incidents
    - Reporters see only their own incidents
    """
    
    is_analyst = current_user.get("role") in ["analyst", "admin"]
    
    result = await get_incidents(
        page=page,
        per_page=per_page,
        incident_type=type,
        severity=severity,
        status=status,
        search=search,
        user_id=current_user.get("id"),
        is_analyst=is_analyst
    )
    
    return IncidentListResponse(**result)


@router.get("/{incident_id}", response_model=IncidentWithAnalysis)
async def get_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get single incident with full analysis
    """
    
    result = await get_incident_by_id(incident_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return IncidentWithAnalysis(
        incident=IncidentResponse(**result["incident"]),
        analysis=AnalysisResult(**result["analysis"]) if result["analysis"] else None
    )


@router.get("/{incident_id}/analysis", response_model=AnalysisResult)
async def get_incident_analysis(
    incident_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get only the analysis for an incident
    """
    
    result = await get_incident_by_id(incident_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    if not result["analysis"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found for this incident"
        )
    
    return AnalysisResult(**result["analysis"])


@router.post("/{incident_id}/escalate", response_model=MessageResponse)
async def escalate_to_cert(
    incident_id: str,
    current_user: dict = Depends(get_analyst_or_admin)
):
    """
    Escalate incident to CERT (Analysts/Admins only)
    """
    
    success = await escalate_incident(incident_id, current_user.get("id"))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to escalate incident"
        )
    
    return MessageResponse(
        success=True,
        message="Incident escalated to CERT-Army successfully"
    )
