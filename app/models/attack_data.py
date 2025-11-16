from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Float, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
class Technique(Base):
    __tablename__ = "techniques"
    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(String(20), unique=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    tactics = Column(ARRAY(String))
    platforms = Column(ARRAY(String))
    detection_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    detection_strategies = relationship("DetectionStrategy", back_populates="technique")
    sub_techniques = relationship("SubTechnique", back_populates="parent_technique")
class SubTechnique(Base):
    __tablename__ = "sub_techniques"
    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(String(20), unique=True, index=True)
    parent_technique_id = Column(String(20), ForeignKey("techniques.technique_id"))
    name = Column(String(255))
    description = Column(Text)
    platforms = Column(ARRAY(String))
    parent_technique = relationship("Technique", back_populates="sub_techniques")
    detection_strategies = relationship("DetectionStrategy", back_populates="sub_technique")
class DetectionStrategy(Base):
    __tablename__ = "detection_strategies"
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String(20), unique=True, index=True)
    technique_id = Column(String(20), ForeignKey("techniques.technique_id"), nullable=True)
    sub_technique_id = Column(String(20), ForeignKey("sub_techniques.technique_id"), nullable=True)
    name = Column(String(255))
    description = Column(Text)
    behavior_to_detect = Column(Text)
    technique = relationship("Technique", back_populates="detection_strategies")
    sub_technique = relationship("SubTechnique", back_populates="detection_strategies")
    analytics = relationship("Analytic", back_populates="detection_strategy")
class Analytic(Base):
    __tablename__ = "analytics"
    id = Column(Integer, primary_key=True, index=True)
    analytic_id = Column(String(20), unique=True, index=True)
    strategy_id = Column(String(20), ForeignKey("detection_strategies.strategy_id"))
    name = Column(String(255))
    description = Column(Text)
    detection_logic = Column(Text)
    platform = Column(String(100))
    data_components_required = Column(ARRAY(String))
    tunable_parameters = Column(JSON)
    detection_strategy = relationship("DetectionStrategy", back_populates="analytics")
class DataComponent(Base):
    __tablename__ = "data_components"
    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(String(20), unique=True, index=True)
    name = Column(String(255))
    description = Column(Text)
    data_source_name = Column(String(255))
    log_source_type = Column(String(100))
    collection_requirements = Column(JSON)
class ThreatGroup(Base):
    __tablename__ = "threat_groups"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String(20), unique=True, index=True)
    name = Column(String(255))
    aliases = Column(ARRAY(String))
    description = Column(Text)
    target_industries = Column(ARRAY(String))
    techniques_used = Column(ARRAY(String))
    