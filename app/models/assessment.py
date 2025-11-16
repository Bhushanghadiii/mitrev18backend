from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY   # <-- ADD THIS LINE!
from datetime import datetime
from app.database import Base
import enum

class CoverageStatus(str, enum.Enum):
    COVERED = "covered"
    PARTIAL = "partial"
    NONE = "none"
    NOT_APPLICABLE = "not_applicable"

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    assessment_name = Column(String(255))
    industry = Column(String(100))
    organization_size = Column(String(50))
    cloud_usage = Column(JSON)
    completion_date = Column(DateTime, nullable=True)
    coverage_percentage = Column(Float, default=0.0)
    status = Column(String(50), default="in_progress")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant = relationship("Tenant", back_populates="assessments")
    responses = relationship("QuestionnaireResponse", back_populates="assessment")
    technique_coverage = relationship("TechniqueCoverage", back_populates="assessment")

class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(String(50))
    capability_type = Column(String(100))
    has_capability = Column(Boolean)
    coverage_level = Column(Integer, default=0)
    platforms_covered = Column(ARRAY(String))      # <-- NOW WORKS!
    notes = Column(Text, nullable=True)
    assessment = relationship("Assessment", back_populates="responses")

class TechniqueCoverage(Base):
    __tablename__ = "technique_coverage"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    technique_id = Column(String(20))
    coverage_status = Column(Enum(CoverageStatus))
    confidence_score = Column(Float, default=0.0)
    strategies_implemented = Column(ARRAY(String))
    analytics_implemented = Column(ARRAY(String))
    data_components_available = Column(ARRAY(String))
    data_components_missing = Column(ARRAY(String))
    risk_score = Column(Float, default=0.0)
    priority_rank = Column(Integer, nullable=True)
    assessment = relationship("Assessment", back_populates="technique_coverage")
