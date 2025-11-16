from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant import User
from app.models.assessment import Assessment
from app.utils.security import get_current_user

router = APIRouter()

@router.get("/{assessment_id}/executive")
async def generate_executive_report(assessment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    return {
        "report_type": "executive",
        "organization": current_user.tenant.org_name,
        "assessment_name": assessment.assessment_name,
        "coverage_percentage": assessment.coverage_percentage,
        "summary": f"Your organization has {assessment.coverage_percentage}% ATT&CK coverage",
        "recommendations": "Implement missing data components to improve detection capabilities"
    }
