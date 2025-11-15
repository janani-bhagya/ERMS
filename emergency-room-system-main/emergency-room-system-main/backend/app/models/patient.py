# backend/app/models/patient.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from app.schemas.patient import ESILevel, PatientStatus
import enum


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    esi_level = Column(Integer, nullable=False)  # 1-5
    chief_complaint = Column(String, nullable=False)
    vital_signs = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="waiting")
    priority_score = Column(Float, nullable=False, default=0.0)
    waiting_time = Column(Integer, nullable=False, default=0)  # minutes
    
    # Room assignment
    assigned_room_id = Column(String, nullable=True)
    assigned_provider_ids = Column(JSON, nullable=True)  # List of provider IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    discharged_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "esi_level": self.esi_level,
            "chief_complaint": self.chief_complaint,
            "vital_signs": self.vital_signs,
            "status": self.status,
            "priority_score": self.priority_score,
            "waiting_time": self.waiting_time,
            "assigned_room_id": self.assigned_room_id,
            "assigned_provider_ids": self.assigned_provider_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "discharged_at": self.discharged_at.isoformat() if self.discharged_at else None,
        }
