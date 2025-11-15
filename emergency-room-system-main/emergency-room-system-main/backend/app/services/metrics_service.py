"""
Metrics Service for recording and calculating patient performance metrics.
Handles door-to-provider time, length of stay, and aggregate statistics.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.metrics import PatientMetrics


class MetricsService:
    """Service for managing patient performance metrics"""
    
    @staticmethod
    def record_arrival(
        db: Session,
        patient_id: str,
        esi_level: int = None,
        chief_complaint: str = None
    ) -> PatientMetrics:
        """
        Record patient arrival time (door time).
        
        Args:
            db: Database session
            patient_id: Unique patient identifier
            esi_level: ESI triage level (1-5)
            chief_complaint: Patient's chief complaint
        
        Returns:
            PatientMetrics object
        """
        metrics = PatientMetrics(
            patient_id=patient_id,
            arrival_time=datetime.now(),
            esi_level=esi_level,
            chief_complaint=chief_complaint
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics
    
    @staticmethod
    def record_triage_complete(
        db: Session,
        patient_id: str
    ) -> Optional[PatientMetrics]:
        """
        Record triage completion time.
        
        Args:
            db: Database session
            patient_id: Unique patient identifier
        
        Returns:
            Updated PatientMetrics object or None
        """
        metrics = db.query(PatientMetrics).filter(
            PatientMetrics.patient_id == patient_id
        ).order_by(PatientMetrics.created_at.desc()).first()
        
        if metrics:
            metrics.triage_complete_time = datetime.now()
            metrics.calculate_metrics()
            db.commit()
            db.refresh(metrics)
            return metrics
        return None
    
    @staticmethod
    def record_provider_contact(
        db: Session,
        patient_id: str
    ) -> Optional[PatientMetrics]:
        """
        Record when provider first contacts patient.
        Critical metric for door-to-provider time.
        
        Args:
            db: Database session
            patient_id: Unique patient identifier
        
        Returns:
            Updated PatientMetrics object or None
        """
        metrics = db.query(PatientMetrics).filter(
            PatientMetrics.patient_id == patient_id
        ).order_by(PatientMetrics.created_at.desc()).first()
        
        if metrics:
            metrics.provider_contact_time = datetime.now()
            metrics.calculate_metrics()
            db.commit()
            db.refresh(metrics)
            return metrics
        return None
    
    @staticmethod
    def record_treatment_start(
        db: Session,
        patient_id: str
    ) -> Optional[PatientMetrics]:
        """
        Record treatment start time.
        
        Args:
            db: Database session
            patient_id: Unique patient identifier
        
        Returns:
            Updated PatientMetrics object or None
        """
        metrics = db.query(PatientMetrics).filter(
            PatientMetrics.patient_id == patient_id
        ).order_by(PatientMetrics.created_at.desc()).first()
        
        if metrics:
            metrics.treatment_start_time = datetime.now()
            metrics.calculate_metrics()
            db.commit()
            db.refresh(metrics)
            return metrics
        return None
    
    @staticmethod
    def record_discharge(
        db: Session,
        patient_id: str
    ) -> Optional[PatientMetrics]:
        """
        Record patient discharge time.
        Completes length of stay calculation.
        
        Args:
            db: Database session
            patient_id: Unique patient identifier
        
        Returns:
            Updated PatientMetrics object or None
        """
        metrics = db.query(PatientMetrics).filter(
            PatientMetrics.patient_id == patient_id
        ).order_by(PatientMetrics.created_at.desc()).first()
        
        if metrics:
            metrics.discharge_time = datetime.now()
            metrics.calculate_metrics()
            db.commit()
            db.refresh(metrics)
            return metrics
        return None
    
    @staticmethod
    def get_patient_metrics(
        db: Session,
        patient_id: str
    ) -> Optional[PatientMetrics]:
        """
        Get metrics for a specific patient.
        
        Args:
            db: Database session
            patient_id: Unique patient identifier
        
        Returns:
            PatientMetrics object or None
        """
        return db.query(PatientMetrics).filter(
            PatientMetrics.patient_id == patient_id
        ).order_by(PatientMetrics.created_at.desc()).first()
    
    @staticmethod
    def calculate_door_to_provider(
        arrival_time: datetime,
        provider_contact_time: datetime
    ) -> int:
        """
        Calculate door-to-provider time in minutes.
        
        Args:
            arrival_time: Patient arrival timestamp
            provider_contact_time: Provider contact timestamp
        
        Returns:
            Minutes between arrival and provider contact
        """
        if not arrival_time or not provider_contact_time:
            return 0
        delta = provider_contact_time - arrival_time
        return int(delta.total_seconds() / 60)
    
    @staticmethod
    def calculate_length_of_stay(
        arrival_time: datetime,
        discharge_time: datetime
    ) -> int:
        """
        Calculate length of stay in minutes.
        
        Args:
            arrival_time: Patient arrival timestamp
            discharge_time: Patient discharge timestamp
        
        Returns:
            Minutes between arrival and discharge
        """
        if not arrival_time or not discharge_time:
            return 0
        delta = discharge_time - arrival_time
        return int(delta.total_seconds() / 60)
    
    @staticmethod
    def get_aggregate_metrics(
        db: Session,
        hours: int = 24
    ) -> Dict:
        """
        Get aggregate metrics for the last N hours.
        
        Args:
            db: Database session
            hours: Number of hours to look back (default: 24)
        
        Returns:
            Dictionary with aggregate statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Query metrics from the last N hours
        recent_metrics = db.query(PatientMetrics).filter(
            PatientMetrics.arrival_time >= cutoff_time
        ).all()
        
        if not recent_metrics:
            return {
                "total_patients": 0,
                "avg_door_to_provider_minutes": None,
                "avg_length_of_stay_minutes": None,
                "avg_door_to_triage_minutes": None,
                "patients_with_complete_metrics": 0,
                "time_window_hours": hours
            }
        
        # Calculate averages
        door_to_provider_times = [
            m.door_to_provider_minutes for m in recent_metrics 
            if m.door_to_provider_minutes is not None
        ]
        
        length_of_stay_times = [
            m.length_of_stay_minutes for m in recent_metrics 
            if m.length_of_stay_minutes is not None
        ]
        
        door_to_triage_times = [
            m.door_to_triage_minutes for m in recent_metrics 
            if m.door_to_triage_minutes is not None
        ]
        
        return {
            "total_patients": len(recent_metrics),
            "avg_door_to_provider_minutes": (
                round(sum(door_to_provider_times) / len(door_to_provider_times), 1)
                if door_to_provider_times else None
            ),
            "avg_length_of_stay_minutes": (
                round(sum(length_of_stay_times) / len(length_of_stay_times), 1)
                if length_of_stay_times else None
            ),
            "avg_door_to_triage_minutes": (
                round(sum(door_to_triage_times) / len(door_to_triage_times), 1)
                if door_to_triage_times else None
            ),
            "patients_with_complete_metrics": len(length_of_stay_times),
            "time_window_hours": hours
        }
    
    @staticmethod
    def get_metrics_by_esi_level(
        db: Session,
        hours: int = 24
    ) -> Dict[int, Dict]:
        """
        Get metrics grouped by ESI level.
        
        Args:
            db: Database session
            hours: Number of hours to look back
        
        Returns:
            Dictionary with ESI levels as keys and metrics as values
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        result = {}
        for esi_level in range(1, 6):  # ESI levels 1-5
            metrics = db.query(PatientMetrics).filter(
                PatientMetrics.arrival_time >= cutoff_time,
                PatientMetrics.esi_level == esi_level
            ).all()
            
            if metrics:
                door_to_provider = [
                    m.door_to_provider_minutes for m in metrics 
                    if m.door_to_provider_minutes is not None
                ]
                
                result[esi_level] = {
                    "count": len(metrics),
                    "avg_door_to_provider": (
                        round(sum(door_to_provider) / len(door_to_provider), 1)
                        if door_to_provider else None
                    )
                }
        
        return result
