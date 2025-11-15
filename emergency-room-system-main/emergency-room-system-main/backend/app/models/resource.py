# backend/app/models/resource.py
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False)
    room_type = Column(String, nullable=False)  # trauma, exam, isolation, etc
    status = Column(String, nullable=False, default="available")
    current_patient_id = Column(String, nullable=True)
    equipment_ids = Column(JSON, nullable=True)  # List of equipment IDs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "room_number": self.room_number,
            "room_type": self.room_type,
            "status": self.status,
            "current_patient_id": self.current_patient_id,
            "equipment_ids": self.equipment_ids or [],
        }


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="available")
    location = Column(String, nullable=True)  # room_id or storage location
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "equipment_type": self.equipment_type,
            "status": self.status,
            "location": self.location,
        }


class Provider(Base):
    __tablename__ = "providers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # physician, nurse, etc
    specialization = Column(String, nullable=True)
    is_available = Column(String, nullable=False, default="true")  # "true" or "false"
    current_patient_ids = Column(JSON, nullable=True)  # List of patient IDs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "specialization": self.specialization,
            "is_available": self.is_available == "true",
            "current_patient_ids": self.current_patient_ids or [],
        }
