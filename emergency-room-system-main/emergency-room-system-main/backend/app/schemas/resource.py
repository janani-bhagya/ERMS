# backend/app/schemas/resource.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoomType(str, Enum):
    TRAUMA = "trauma"
    EXAM = "exam"
    ISOLATION = "isolation"
    OBSERVATION = "observation"
    PROCEDURE = "procedure"


class RoomStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"


class EquipmentType(str, Enum):
    VENTILATOR = "ventilator"
    MONITOR = "monitor"
    DEFIBRILLATOR = "defibrillator"
    INFUSION_PUMP = "infusion_pump"
    ULTRASOUND = "ultrasound"
    XRAY = "xray"


class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class ProviderRole(str, Enum):
    PHYSICIAN = "physician"
    NURSE = "nurse"
    RESIDENT = "resident"
    SPECIALIST = "specialist"
    TECHNICIAN = "technician"


class Room(BaseModel):
    id: str
    room_number: str
    room_type: RoomType
    status: RoomStatus
    current_patient_id: Optional[str] = None
    equipment_ids: List[str] = []


class Equipment(BaseModel):
    id: str
    name: str
    equipment_type: EquipmentType
    status: EquipmentStatus
    location: Optional[str] = None  # room_id or storage location


class Provider(BaseModel):
    id: str
    name: str
    role: ProviderRole
    specialization: Optional[str] = None
    is_available: bool = True
    current_patient_ids: List[str] = []


class LabTestRequest(BaseModel):
    patient_id: str
    test_type: str
    priority: int  # 1-10, higher = more urgent
    requested_by: str
    notes: Optional[str] = None


class ResourceAllocation(BaseModel):
    patient_id: str
    room_id: Optional[str] = None
    provider_ids: List[str] = []
    equipment_ids: List[str] = []
