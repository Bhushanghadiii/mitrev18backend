from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from app.database import get_db
from app.models.tenant import User
from app.models.assessment import Assessment
from app.utils.security import get_current_user

router = APIRouter()

class CreateAssessmentRequest(BaseModel):
    assessment_name: str
    organization_size: str
    cloud_usage: Optional[Dict] = {}

class AssessmentResponse(BaseModel):
    id: int
    assessment_name: str
    industry: str
    organization_size: str
    cloud_usage: Optional[Dict] = {}
    coverage_percentage: float = 0.0
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    request: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = Assessment(
        tenant_id=current_user.tenant_id,
        assessment_name=request.assessment_name,
        industry=current_user.tenant.industry,
        organization_size=request.organization_size,
        cloud_usage=request.cloud_usage,
        status="in_progress",
        created_at=datetime.utcnow()
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/", response_model=List[AssessmentResponse])
async def list_assessments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessments = db.query(Assessment)\
        .filter(Assessment.tenant_id == current_user.tenant_id)\
        .order_by(Assessment.created_at.desc())\
        .all()
    return assessments


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.tenant_id == current_user.tenant_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment
