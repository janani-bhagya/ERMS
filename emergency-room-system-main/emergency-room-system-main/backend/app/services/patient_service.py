from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import uuid

from app.models.patient import Patient
from app.schemas.patient import PatientStatus


class PatientService:
    def __init__(self):
        self._counter = 0

    def _generate_id(self) -> str:
        """Generate unique patient ID"""
        return f"PAT{str(uuid.uuid4())[:8].upper()}"

    def create_patient(self, patient_input: Dict[str, Any], db: Session) -> str:
        """Create and store a patient record in database. Returns patient_id."""
        patient_id = self._generate_id()

        patient = Patient(
            id=patient_id,
            name=patient_input.get("name"),
            age=patient_input.get("age"),
            esi_level=patient_input.get("esi_level"),
            chief_complaint=patient_input.get("chief_complaint"),
            vital_signs=patient_input.get("vital_signs", {}),
            status="waiting",
            priority_score=0.0,
            waiting_time=0,
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        return patient_id

    def get_patient(self, patient_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get patient record from database"""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        return patient.to_dict() if patient else None

    def update_patient(self, patient_id: str, updates: Dict[str, Any], db: Session) -> bool:
        """Update patient record in database"""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return False

        # Apply updates
        for key, value in updates.items():
            if key == "id":  # Don't allow changing id
                continue
            if hasattr(patient, key):
                setattr(patient, key, value)

        db.commit()
        return True

    def delete_patient(self, patient_id: str, db: Session) -> bool:
        """Delete patient record from database"""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return False
        
        db.delete(patient)
        db.commit()
        return True

    def list_all_patients(self, db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all patients, optionally filtered by status"""
        query = db.query(Patient)
        
        if status:
            query = query.filter(Patient.status == status)
        
        patients = query.all()
        return [p.to_dict() for p in patients]

    def discharge_patient(self, patient_id: str, db: Session) -> bool:
        """Discharge patient (set status and timestamp)"""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return False
        
        patient.status = "discharged"
        patient.discharged_at = datetime.utcnow()
        
        db.commit()
        return True

