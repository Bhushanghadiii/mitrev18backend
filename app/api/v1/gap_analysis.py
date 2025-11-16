from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.tenant import User
from app.models.assessment import TechniqueCoverage, CoverageStatus
from app.services.assessment_engine import AssessmentEngine
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/{assessment_id}/calculate")
async def calculate_gap_analysis(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    engine = AssessmentEngine(db)
    result = engine.calculate_coverage(assessment_id)
    return result

@router.get("/{assessment_id}/coverage")
async def get_coverage_matrix(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    coverage = db.query(TechniqueCoverage).filter(
        TechniqueCoverage.assessment_id == assessment_id
    ).all()
    return {
        "assessment_id": assessment_id,
        "techniques": [
            {
                "technique_id": c.technique_id,
                "coverage_status": getattr(c.coverage_status, "value", str(c.coverage_status)),
                "confidence_score": c.confidence_score,
                "risk_score": c.risk_score
            }
            for c in coverage
        ]
    }

@router.get("/{assessment_id}/gaps")
async def get_prioritized_gaps(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    gaps = db.query(TechniqueCoverage).filter(
        TechniqueCoverage.assessment_id == assessment_id,
        TechniqueCoverage.coverage_status.in_([CoverageStatus.NONE, CoverageStatus.PARTIAL])
    ).order_by(TechniqueCoverage.risk_score.desc()).limit(20).all()
    return {
        "top_gaps": [
            {
                "technique_id": g.technique_id,
                "coverage_status": getattr(g.coverage_status, "value", str(g.coverage_status)),
                "risk_score": g.risk_score,
                "missing_components": g.data_components_missing or []
            }
            for g in gaps
        ]
    }
