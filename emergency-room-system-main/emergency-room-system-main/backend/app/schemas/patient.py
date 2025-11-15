# backend/app/schemas/patient.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ESILevel(int, Enum):
    LEVEL_1 = 1  # Resuscitation
    LEVEL_2 = 2  # Emergency
    LEVEL_3 = 3  # Urgent
    LEVEL_4 = 4  # Less Urgent
    LEVEL_5 = 5  # Non-Urgent

class PatientStatus(str, Enum):
    WAITING = "waiting"
    IN_TREATMENT = "in_treatment"
    DISCHARGED = "discharged"
    ADMITTED = "admitted"

class PatientBase(BaseModel):
    name: str
    age: int
    esi_level: ESILevel
    chief_complaint: str
    vital_signs: Dict[str, Any]

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: str
    status: PatientStatus
    priority_score: float
    waiting_time: int  # in minutes
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TriageUpdate(BaseModel):
    patient_id: str
    new_esi_level: ESILevel
    new_vital_signs: Dict[str, Any]
