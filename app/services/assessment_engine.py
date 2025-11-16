from sqlalchemy.orm import Session
from app.models.assessment import TechniqueCoverage, Assessment, QuestionnaireResponse, CoverageStatus
from app.models.attack_data import Technique  # adjust as needed
from datetime import datetime

class AssessmentEngine:
    def __init__(self, db: Session):
        self.db = db

    def calculate_coverage(self, assessment_id: int):
        # 1. Clear previous coverage
        self.db.query(TechniqueCoverage).filter(TechniqueCoverage.assessment_id == assessment_id).delete()

        # 2. Get all techniques
        techniques = self.db.query(Technique).all()
        responses = self.db.query(QuestionnaireResponse).filter_by(assessment_id=assessment_id).all()
        answers = {r.question_id: r for r in responses}

        covered = 0
        for t in techniques:
            # Sample logic: mark COVERED if any questionnaire response has_capability==True for this technique
            q = answers.get(t.technique_id)
            if q is not None and q.has_capability:
                cov_status = CoverageStatus.COVERED
                covered += 1
            else:
                cov_status = CoverageStatus.NONE

            coverage = TechniqueCoverage(
                assessment_id=assessment_id,
                technique_id=t.technique_id,
                coverage_status=cov_status,
                confidence_score=1.0 if cov_status == CoverageStatus.COVERED else 0.0,
                risk_score=5.0 if cov_status == CoverageStatus.NONE else 1.0,
                data_components_missing=[],
                strategies_implemented=[],
                analytics_implemented=[],
                data_components_available=[],
                priority_rank=None
            )
            self.db.add(coverage)

        # 3. Update assessment stats
        total = len(techniques)
        coverage_percent = (covered / total) * 100 if total > 0 else 0
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if assessment:
            assessment.coverage_percentage = coverage_percent
            assessment.updated_at = datetime.utcnow()

        self.db.commit()
        return {"message": "Coverage calculated", "coverage_percentage": coverage_percent}
