"""
Metrics Model for tracking ER performance metrics.
Tracks door-to-provider time, length of stay, and other performance indicators.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime


class PatientMetrics(Base):
    """
    Tracks performance metrics for each patient visit.
    
    Key metrics:
    - Door-to-provider time: Time from arrival to provider contact
    - Length of stay: Total time in ER from arrival to discharge
    """
    __tablename__ = "patient_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String, nullable=False, index=True)
    
    # Key timestamps
    arrival_time = Column(DateTime(timezone=True), nullable=False)
    triage_complete_time = Column(DateTime(timezone=True), nullable=True)
    provider_contact_time = Column(DateTime(timezone=True), nullable=True)
    treatment_start_time = Column(DateTime(timezone=True), nullable=True)
    discharge_time = Column(DateTime(timezone=True), nullable=True)
    
    # Calculated metrics (in minutes)
    door_to_triage_minutes = Column(Integer, nullable=True)
    door_to_provider_minutes = Column(Integer, nullable=True)
    door_to_treatment_minutes = Column(Integer, nullable=True)
    length_of_stay_minutes = Column(Integer, nullable=True)
    
    # Additional context
    esi_level = Column(Integer, nullable=True)  # 1-5
    chief_complaint = Column(String, nullable=True)
    
    # System timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def calculate_metrics(self):
        """Calculate all time-based metrics in minutes"""
        if self.arrival_time:
            if self.triage_complete_time:
                delta = self.triage_complete_time - self.arrival_time
                self.door_to_triage_minutes = int(delta.total_seconds() / 60)
            
            if self.provider_contact_time:
                delta = self.provider_contact_time - self.arrival_time
                self.door_to_provider_minutes = int(delta.total_seconds() / 60)
            
            if self.treatment_start_time:
                delta = self.treatment_start_time - self.arrival_time
                self.door_to_treatment_minutes = int(delta.total_seconds() / 60)
            
            if self.discharge_time:
                delta = self.discharge_time - self.arrival_time
                self.length_of_stay_minutes = int(delta.total_seconds() / 60)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "triage_complete_time": self.triage_complete_time.isoformat() if self.triage_complete_time else None,
            "provider_contact_time": self.provider_contact_time.isoformat() if self.provider_contact_time else None,
            "treatment_start_time": self.treatment_start_time.isoformat() if self.treatment_start_time else None,
            "discharge_time": self.discharge_time.isoformat() if self.discharge_time else None,
            "door_to_triage_minutes": self.door_to_triage_minutes,
            "door_to_provider_minutes": self.door_to_provider_minutes,
            "door_to_treatment_minutes": self.door_to_treatment_minutes,
            "length_of_stay_minutes": self.length_of_stay_minutes,
            "esi_level": self.esi_level,
            "chief_complaint": self.chief_complaint,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
