"""
Metrics Routes for tracking and retrieving patient performance metrics.
Provides endpoints for recording timestamps and calculating metrics.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


class MetricTimestampRequest(BaseModel):
    """Request model for recording metric timestamps"""
    patient_id: str
    milestone: str  # arrival, triage_complete, provider_contact, treatment_start, discharge
    esi_level: Optional[int] = None
    chief_complaint: Optional[str] = None


@router.post("/record")
async def record_metric_timestamp(
    request: MetricTimestampRequest,
    db: Session = Depends(get_db)
):
    """
    Record a timestamp milestone for a patient.
    
    Milestones:
    - arrival: Patient arrives at ER (door time)
    - triage_complete: Triage assessment complete
    - provider_contact: Provider first sees patient
    - treatment_start: Treatment begins
    - discharge: Patient leaves ER
    """
    try:
        if request.milestone == "arrival":
            metrics = MetricsService.record_arrival(
                db, 
                request.patient_id, 
                request.esi_level, 
                request.chief_complaint
            )
        elif request.milestone == "triage_complete":
            metrics = MetricsService.record_triage_complete(db, request.patient_id)
        elif request.milestone == "provider_contact":
            metrics = MetricsService.record_provider_contact(db, request.patient_id)
        elif request.milestone == "treatment_start":
            metrics = MetricsService.record_treatment_start(db, request.patient_id)
        elif request.milestone == "discharge":
            metrics = MetricsService.record_discharge(db, request.patient_id)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid milestone: {request.milestone}"
            )
        
        if not metrics:
            raise HTTPException(
                status_code=404, 
                detail=f"Patient {request.patient_id} not found in metrics"
            )
        
        return {
            "message": f"Recorded {request.milestone} for patient {request.patient_id}",
            "metrics": metrics.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording metric: {str(e)}")


@router.get("/patient/{patient_id}")
async def get_patient_metrics(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for a specific patient.
    
    Returns:
    - All timestamp milestones
    - Calculated metrics (door-to-provider, length of stay, etc.)
    """
    try:
        metrics = MetricsService.get_patient_metrics(db, patient_id)
        
        if not metrics:
            raise HTTPException(
                status_code=404, 
                detail=f"No metrics found for patient {patient_id}"
            )
        
        return {
            "patient_id": patient_id,
            "metrics": metrics.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metrics: {str(e)}")


@router.get("/aggregate")
async def get_aggregate_metrics(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get aggregate performance metrics for the last N hours.
    
    Args:
        hours: Number of hours to look back (default: 24)
    
    Returns:
    - Total patients
    - Average door-to-provider time
    - Average length of stay
    - Other aggregate statistics
    """
    try:
        if hours < 1 or hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=400, 
                detail="Hours must be between 1 and 168 (1 week)"
            )
        
        aggregates = MetricsService.get_aggregate_metrics(db, hours)
        
        return {
            "time_window": f"Last {hours} hours",
            "statistics": aggregates
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating aggregates: {str(e)}")


@router.get("/by-esi-level")
async def get_metrics_by_esi_level(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get metrics grouped by ESI triage level.
    
    Args:
        hours: Number of hours to look back (default: 24)
    
    Returns:
        Dictionary with ESI levels (1-5) as keys and metrics as values
    """
    try:
        if hours < 1 or hours > 168:
            raise HTTPException(
                status_code=400, 
                detail="Hours must be between 1 and 168 (1 week)"
            )
        
        metrics_by_esi = MetricsService.get_metrics_by_esi_level(db, hours)
        
        return {
            "time_window": f"Last {hours} hours",
            "metrics_by_esi_level": metrics_by_esi
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving ESI metrics: {str(e)}")
