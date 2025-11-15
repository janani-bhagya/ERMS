# backend/app/init_db.py
"""
Initialize database tables and seed initial data
Run this script once to set up the database
"""
from app.core.database import engine, Base, SessionLocal
from app.models import Patient, TreatmentHistory, Room, Equipment, Provider
from app.models.metrics import PatientMetrics
import uuid


def init_db():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_resources():
    """Seed initial resources (rooms, equipment, providers)"""
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing_rooms = db.query(Room).count()
        if existing_rooms > 0:
            print("✓ Database already seeded")
            return
        
        print("Seeding initial resources...")
        
        # Seed rooms
        rooms = [
            Room(id="ROOM001", room_number="ER-1", room_type="trauma", status="available"),
            Room(id="ROOM002", room_number="ER-2", room_type="exam", status="available"),
            Room(id="ROOM003", room_number="ER-3", room_type="isolation", status="available"),
            Room(id="ROOM004", room_number="ER-4", room_type="observation", status="available"),
            Room(id="ROOM005", room_number="ER-5", room_type="procedure", status="available"),
        ]
        db.add_all(rooms)
        
        # Seed equipment
        equipment = [
            Equipment(id="EQ001", name="Ventilator-1", equipment_type="ventilator", status="available"),
            Equipment(id="EQ002", name="Ventilator-2", equipment_type="ventilator", status="available"),
            Equipment(id="EQ003", name="Monitor-1", equipment_type="monitor", status="available"),
            Equipment(id="EQ004", name="Monitor-2", equipment_type="monitor", status="available"),
            Equipment(id="EQ005", name="Monitor-3", equipment_type="monitor", status="available"),
            Equipment(id="EQ006", name="Defibrillator-1", equipment_type="defibrillator", status="available"),
            Equipment(id="EQ007", name="Ultrasound-1", equipment_type="ultrasound", status="available"),
            Equipment(id="EQ008", name="Infusion-Pump-1", equipment_type="infusion_pump", status="available"),
            Equipment(id="EQ009", name="Infusion-Pump-2", equipment_type="infusion_pump", status="available"),
        ]
        db.add_all(equipment)
        
        # Seed providers
        providers = [
            Provider(id="DR001", name="Dr. Sarah Smith", role="physician", specialization="Emergency Medicine", is_available="true"),
            Provider(id="DR002", name="Dr. James Chen", role="physician", specialization="Trauma Surgery", is_available="true"),
            Provider(id="DR003", name="Dr. Emily Johnson", role="resident", specialization="Emergency Medicine", is_available="true"),
            Provider(id="NR001", name="Nurse Maria Garcia", role="nurse", is_available="true"),
            Provider(id="NR002", name="Nurse John Williams", role="nurse", is_available="true"),
            Provider(id="NR003", name="Nurse Lisa Brown", role="nurse", is_available="true"),
            Provider(id="NR004", name="Nurse David Lee", role="nurse", is_available="true"),
            Provider(id="TECH001", name="Tech Alex Rivera", role="technician", specialization="Radiology", is_available="true"),
            Provider(id="TECH002", name="Tech Sam Taylor", role="technician", specialization="Laboratory", is_available="true"),
        ]
        db.add_all(providers)
        
        db.commit()
        print(f"✓ Seeded {len(rooms)} rooms, {len(equipment)} equipment, {len(providers)} providers")
        
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing Emergency Room Management System Database...")
    print("=" * 60)
    init_db()
    seed_resources()
    print("=" * 60)
    print("✓ Database initialization complete!")
