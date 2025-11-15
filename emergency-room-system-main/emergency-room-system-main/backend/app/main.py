# backend/app/main.py
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
import socketio

from app.core.database import get_db
from app.models.resource import Room, Provider
from app.services.patient_service import PatientService
from app.services.triage_service import TriageService
from app.services.resource_service import ResourceService
from app.services.treatment_history_service import TreatmentHistoryService
from app.services.websocket_service import WebSocketService
from app.services.waiting_room_service import WaitingRoomService
from app.services.risk_scoring_service import RiskScoringService
from app.schemas.patient import PatientCreate
from app.schemas.treatment import TreatmentActionCreate, TreatmentActionUndo
from app.schemas.resource import LabTestRequest

# Import route modules
from app.routes import metrics_routes, graph_routes

# Global services
triage_service = TriageService()
patient_service = PatientService()
treatment_history_service = TreatmentHistoryService()
resource_service = ResourceService()
websocket_service = WebSocketService()
waiting_room_service = WaitingRoomService()
risk_scoring_service = RiskScoringService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Emergency Room Management System...")
    print("Database connection established")
    print("WebSocket server initialized")
    yield
    print("Shutting down Emergency Room Management System...")

fastapi_app = FastAPI(
    title="Emergency Room Management System",
    description="Intelligent ER management with optimized data structures and PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
fastapi_app.include_router(metrics_routes.router)
fastapi_app.include_router(graph_routes.router)

@fastapi_app.get("/")
async def root():
    return {"message": "Emergency Room Management System API v2.0", "database": "PostgreSQL"}

@fastapi_app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "version": "2.0.0", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

@fastapi_app.post("/patients")
async def add_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    try:
        patient_data = patient.dict()
        patient_id = patient_service.create_patient(patient_data, db)
        priority_score = triage_service.calculate_priority_score(patient_data['esi_level'], 0, patient_data['vital_signs'])
        patient_service.update_patient(patient_id, {"priority_score": priority_score}, db)
        patient_data_with_id = dict(patient_data)
        patient_data_with_id["id"] = patient_id
        patient_data_with_id["priority_score"] = priority_score
        triage_service.add_patient(patient_data_with_id)
        
        # Broadcast WebSocket update
        await websocket_service.broadcast_patient_update({
            "id": patient_id,
            "action": "created",
            "patient": patient_service.get_patient(patient_id, db)
        })
        
        return {"patient_id": patient_id, "priority_score": priority_score, "message": "Patient added to triage system"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")

@fastapi_app.get("/patients/{patient_id}")
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    record = patient_service.get_patient(patient_id, db)
    if not record:
        raise HTTPException(status_code=404, detail="Patient not found")
    return record

@fastapi_app.get("/patients")
async def list_patients(status: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        patients = patient_service.list_all_patients(db, status)
        return {"patients": patients, "count": len(patients)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing patients: {str(e)}")

@fastapi_app.put("/patients/{patient_id}/start-treatment")
async def start_treatment(patient_id: str, db: Session = Depends(get_db)):
    """
    Start treatment for a patient - updates status to in_treatment.
    Requires patient to have a room and at least one provider assigned.
    """
    patient = patient_service.get_patient(patient_id, db)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if patient.get("status") == "in_treatment":
        raise HTTPException(status_code=400, detail="Patient already in treatment")
    
    if patient.get("status") == "discharged":
        raise HTTPException(status_code=400, detail="Patient already discharged")
    
    # Validate resource allocation - Room required
    assigned_room_id = patient.get("assigned_room_id")
    if not assigned_room_id:
        raise HTTPException(
            status_code=400, 
            detail="Cannot start treatment: Patient must be assigned to a room first. Please use the 'Allocate Resources' feature in the Resources page to assign a room and providers before starting treatment."
        )
    
    # Verify room exists and is occupied by this patient
    room = db.query(Room).filter(Room.id == assigned_room_id).first()
    if not room:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start treatment: Assigned room {assigned_room_id} not found in system."
        )
    
    if room.current_patient_id != patient_id:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start treatment: Room {room.room_number} is not properly allocated to this patient. Please reallocate resources."
        )
    
    # Validate provider assignment - At least one provider required
    providers_with_patient = db.query(Provider).filter(
        Provider.current_patient_ids.contains([patient_id])
    ).all()
    
    if not providers_with_patient or len(providers_with_patient) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start treatment: Patient must have at least one healthcare provider assigned. Current room: {room.room_number}. Please use the 'Allocate Resources' feature to assign providers (doctors/nurses) before starting treatment."
        )
    
    # Get provider names for confirmation message
    provider_names = [p.name for p in providers_with_patient]
    provider_summary = ", ".join(provider_names[:3])
    if len(provider_names) > 3:
        provider_summary += f" and {len(provider_names) - 3} more"
    
    try:
        # Update patient status
        patient_service.update_patient(patient_id, {"status": "in_treatment"}, db)
        
        # Broadcast WebSocket update
        await websocket_service.broadcast_patient_update({
            "id": patient_id,
            "action": "treatment_started",
            "patient": patient_service.get_patient(patient_id, db)
        })
        
        return {
            "message": "Treatment started successfully", 
            "patient_id": patient_id,
            "status": "in_treatment",
            "room": room.room_number,
            "providers": provider_names,
            "summary": f"Patient now in treatment at {room.room_number} with {provider_summary}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting treatment: {str(e)}")

@fastapi_app.delete("/patients/{patient_id}/discharge")
async def discharge_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(patient_id, db)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        if patient.get("assigned_room_id"):
            resource_service.release_room(patient["assigned_room_id"], db)
        patient_service.discharge_patient(patient_id, db)
        return {"message": "Patient discharged successfully", "patient_id": patient_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discharging patient: {str(e)}")

@fastapi_app.get("/patients/triage/next")
async def get_next_patient(db: Session = Depends(get_db)):
    next_patient = triage_service.get_next_patient()
    if next_patient:
        priority, patient_id, clinical_data = next_patient
        patient_service.update_patient(patient_id, {"status": "in_treatment"}, db)
        return {"patient_id": patient_id, "priority": priority, "clinical_data": clinical_data}
    return {"message": "No patients in queue"}

@fastapi_app.get("/triage/status")
async def get_triage_status():
    return {"patients_waiting": triage_service.heap.size(), "system_status": "operational"}

@fastapi_app.post("/treatments")
async def add_treatment_action(action: TreatmentActionCreate, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(action.patient_id, db)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        action_data = action.dict()
        patient_id = action_data.pop("patient_id")
        action_record = treatment_history_service.add_action(patient_id, action_data, db)
        return {"message": "Treatment action recorded", "action": action_record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding treatment action: {str(e)}")

@fastapi_app.delete("/treatments/undo")
async def undo_treatment_action(undo_request: TreatmentActionUndo, db: Session = Depends(get_db)):
    try:
        undone_action = treatment_history_service.undo_last_action(undo_request.patient_id, db)
        if not undone_action:
            raise HTTPException(status_code=404, detail="No action to undo")
        return {"message": "Action undone", "undone_action": undone_action}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error undoing action: {str(e)}")

@fastapi_app.get("/treatments/{patient_id}/history")
async def get_treatment_history(patient_id: str, include_undone: bool = False, db: Session = Depends(get_db)):
    try:
        history = treatment_history_service.get_full_history(patient_id, db, include_undone)
        return {"patient_id": patient_id, "history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")

@fastapi_app.get("/rooms")
async def get_rooms(include_occupied: Optional[bool] = True, room_type: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all rooms or filter by availability"""
    try:
        if include_occupied:
            # Get all rooms
            from app.models.resource import Room
            query = db.query(Room)
            if room_type:
                query = query.filter(Room.room_type == room_type)
            rooms = query.all()
            return {
                "rooms": [
                    {
                        "id": r.id,
                        "room_number": r.room_number,
                        "room_type": r.room_type,
                        "status": r.status,
                        "current_patient_id": r.current_patient_id,
                        "equipment_ids": r.equipment_ids or []
                    }
                    for r in rooms
                ],
                "count": len(rooms)
            }
        else:
            # Get only available rooms
            rooms = resource_service.get_available_rooms(db, room_type)
            return {"rooms": rooms, "count": len(rooms)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rooms: {str(e)}")

@fastapi_app.post("/rooms/{room_id}/assign")
async def assign_room(room_id: str, patient_id: str, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(patient_id, db)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    success = resource_service.assign_room(room_id, patient_id, db)
    if not success:
        raise HTTPException(status_code=400, detail="Room unavailable or not found")
    patient_service.update_patient(patient_id, {"assigned_room_id": room_id}, db)
    return {"message": "Room assigned", "room_id": room_id, "patient_id": patient_id}

@fastapi_app.get("/providers")
async def get_providers(include_busy: Optional[bool] = True, role: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all providers or filter by availability"""
    try:
        from app.models.resource import Provider
        
        if include_busy:
            # Get all providers
            query = db.query(Provider)
            if role:
                query = query.filter(Provider.role == role)
            providers = query.all()
            return {
                "providers": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "role": p.role,
                        "specialization": p.specialization,
                        "is_available": p.is_available == "true" or p.is_available == True,
                        "current_patient_ids": p.current_patient_ids or []
                    }
                    for p in providers
                ],
                "count": len(providers)
            }
        else:
            # Get only available providers
            providers = resource_service.get_available_providers(db, role)
            return {"providers": providers, "count": len(providers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")

@fastapi_app.get("/metrics/resource-utilization")
async def get_resource_utilization(db: Session = Depends(get_db)):
    try:
        from app.models.resource import Room, Equipment, Provider
        total_rooms = db.query(Room).count()
        occupied_rooms = db.query(Room).filter(Room.status == "occupied").count()
        total_equipment = db.query(Equipment).count()
        in_use_equipment = db.query(Equipment).filter(Equipment.status == "in_use").count()
        total_providers = db.query(Provider).count()
        busy_providers = db.query(Provider).filter(Provider.is_available == "false").count()
        return {
            "rooms": {"total": total_rooms, "occupied": occupied_rooms, "utilization_rate": round(occupied_rooms / total_rooms * 100, 2) if total_rooms > 0 else 0},
            "equipment": {"total": total_equipment, "in_use": in_use_equipment, "utilization_rate": round(in_use_equipment / total_equipment * 100, 2) if total_equipment > 0 else 0},
            "providers": {"total": total_providers, "busy": busy_providers, "utilization_rate": round(busy_providers / total_providers * 100, 2) if total_providers > 0 else 0}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating utilization: {str(e)}")

# Resource Allocation Endpoint
@fastapi_app.post("/resources/allocate")
async def allocate_resources(
    patient_id: str,
    room_id: str,
    provider_ids: list[str],
    db: Session = Depends(get_db)
):
    """
    Allocate room and providers to a patient and update resource statuses
    """
    try:
        from app.models.patient import Patient
        from app.models.resource import Room, Provider
        
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get room
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Check if room is available
        if room.current_patient_id and room.current_patient_id != patient_id:
            raise HTTPException(status_code=400, detail="Room is already occupied")
        
        # Assign patient to room
        patient.assigned_room_id = room_id
        patient.assigned_provider_ids = provider_ids
        patient.status = "in_treatment"
        
        # Update room status
        room.current_patient_id = patient_id
        room.status = "occupied"
        
        # Update provider statuses
        for provider_id in provider_ids:
            provider = db.query(Provider).filter(Provider.id == provider_id).first()
            if provider:
                if not provider.current_patient_ids:
                    provider.current_patient_ids = []
                if patient_id not in provider.current_patient_ids:
                    provider.current_patient_ids.append(patient_id)
                provider.is_available = "false"  # Store as string in database
        
        db.commit()
        db.refresh(patient)
        
        return {
            "message": "Resources allocated successfully",
            "patient_id": patient_id,
            "room_id": room_id,
            "provider_ids": provider_ids
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error allocating resources: {str(e)}")

# Waiting Room Queue Endpoints
@fastapi_app.post("/waiting-room/add")
async def add_to_waiting_room(patient_id: str, db: Session = Depends(get_db)):
    """Add patient to waiting room queue with priority based on ESI level"""
    try:
        patient = patient_service.get_patient(patient_id, db)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Calculate priority score (higher ESI level = more urgent)
        # ESI 1 (immediate) = highest priority, ESI 5 (non-urgent) = lowest
        priority_score = patient.get("priority_score", 0)
        
        result = waiting_room_service.add_to_waiting_room(patient_id, priority_score, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to waiting room: {str(e)}")

@fastapi_app.get("/waiting-room/next")
async def get_next_patient():
    """Get next patient from waiting room queue (highest priority)"""
    try:
        patient_id = waiting_room_service.get_next_patient()
        if not patient_id:
            return {"message": "No patients in waiting room"}
        return {"patient_id": patient_id, "message": "Next patient retrieved from queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting next patient: {str(e)}")

@fastapi_app.get("/waiting-room/status")
async def get_waiting_room_status(db: Session = Depends(get_db)):
    """Get current status of waiting room queue"""
    try:
        status = waiting_room_service.get_queue_status(db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting waiting room status: {str(e)}")

@fastapi_app.delete("/waiting-room/remove/{patient_id}")
async def remove_from_waiting_room(patient_id: str):
    """Remove patient from waiting room queue"""
    try:
        success = waiting_room_service.remove_patient(patient_id)
        if not success:
            raise HTTPException(status_code=404, detail="Patient not in waiting room")
        return {"message": "Patient removed from waiting room"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing patient: {str(e)}")

@fastapi_app.get("/waiting-room/estimate/{patient_id}")
async def get_estimated_wait_time(patient_id: str):
    """Get estimated wait time for patient in waiting room"""
    try:
        wait_time = waiting_room_service.get_estimated_wait_time(patient_id)
        if wait_time is None:
            raise HTTPException(status_code=404, detail="Patient not in waiting room")
        return {
            "patient_id": patient_id,
            "estimated_wait_minutes": wait_time,
            "message": f"Estimated wait time: {wait_time} minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating wait time: {str(e)}")

# Risk Scoring / Predictive Analytics Endpoints
@fastapi_app.post("/risk-assessment/calculate")
async def calculate_patient_risk(patient_data: dict):
    """Calculate deterioration risk score for patient data"""
    try:
        # Note: db parameter not needed for calculation-only endpoint
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            risk_assessment = risk_scoring_service.calculate_risk_score(patient_data, db)
            return risk_assessment
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating risk: {str(e)}")

@fastapi_app.get("/risk-assessment/patient/{patient_id}")
async def get_patient_risk_assessment(patient_id: str, db: Session = Depends(get_db)):
    """Get risk assessment for existing patient"""
    try:
        risk_assessment = risk_scoring_service.update_patient_risk(patient_id, db)
        if not risk_assessment:
            raise HTTPException(status_code=404, detail="Patient not found")
        return risk_assessment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assessing patient risk: {str(e)}")

@fastapi_app.post("/risk-assessment/batch")
async def batch_risk_assessment(db: Session = Depends(get_db)):
    """Calculate risk scores for all patients in waiting status"""
    try:
        from app.models.patient import Patient
        
        # Get all waiting or in-treatment patients
        patients = db.query(Patient).filter(
            Patient.status.in_(['waiting', 'in_treatment'])
        ).all()
        
        results = []
        for patient in patients:
            risk_assessment = risk_scoring_service.update_patient_risk(patient.id, db)
            if risk_assessment:
                results.append({
                    'patient_id': patient.id,
                    'name': patient.name,
                    'risk_assessment': risk_assessment
                })
        
        return {
            'total_patients': len(results),
            'assessments': results,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch assessment: {str(e)}")

# Create the combined ASGI application
# Wrap FastAPI app with Socket.IO - this becomes the main app
app = socketio.ASGIApp(
    websocket_service.sio,
    other_asgi_app=fastapi_app,
    socketio_path='/socket.io'
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)