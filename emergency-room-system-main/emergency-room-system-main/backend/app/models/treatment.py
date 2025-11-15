# backend/app/models/treatment.py
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class TreatmentHistory(Base):
    __tablename__ = "treatment_history"

    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False)
    performed_by = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # For undo tracking
    is_undone = Column(String, nullable=False, default="false")  # "true" or "false"
    undone_at = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "action_type": self.action_type,
            "performed_by": self.performed_by,
            "details": self.details,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_undone": self.is_undone == "true",
            "undone_at": self.undone_at.isoformat() if self.undone_at else None,
        }
