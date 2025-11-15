# backend/app/schemas/treatment.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TreatmentActionType(str, Enum):
    MEDICATION_GIVEN = "medication_given"
    VITAL_SIGNS_UPDATE = "vital_signs_update"
    PROCEDURE_PERFORMED = "procedure_performed"
    DIAGNOSIS_UPDATE = "diagnosis_update"
    STATUS_CHANGE = "status_change"
    NOTE_ADDED = "note_added"


class TreatmentAction(BaseModel):
    action_type: TreatmentActionType
    timestamp: datetime
    performed_by: str  # staff member ID or name
    details: Dict[str, Any]
    notes: Optional[str] = None


class TreatmentActionCreate(BaseModel):
    patient_id: str
    action_type: TreatmentActionType
    performed_by: str
    details: Dict[str, Any]
    notes: Optional[str] = None


class TreatmentActionUndo(BaseModel):
    patient_id: str
