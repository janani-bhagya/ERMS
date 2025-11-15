# backend/app/services/waiting_room_service.py
"""
Waiting Room Queue Service - Implements Queue data structure for patient waiting room management
Addresses proposal Section 6.4: "FIFO processing of patients by stages of treatment with priority insertion"

This service uses the PriorityQueue data structure to manage patients in the waiting room,
ensuring FIFO (First-In-First-Out) processing while allowing priority-based insertion for urgent cases.
"""
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.queue import PriorityQueue
from app.models.patient import Patient


class WaitingRoomService:
    """
    Manages the waiting room queue using FIFO processing with priority insertion.
    Implements Queue data structure requirement from proposal Section 6.4.
    """
    
    def __init__(self):
        self.waiting_queue = PriorityQueue()
        self._queue_cache = {}  # Track patients in queue with metadata
    
    def add_to_waiting_room(self, patient_id: str, priority_score: float, db: Session) -> Dict:
        """
        Add patient to waiting room queue with priority.
        Higher priority score = higher urgency (treated first).
        
        Args:
            patient_id: Patient identifier
            priority_score: Priority score (higher = more urgent)
            db: Database session
        
        Returns:
            Dict with status, position in queue, and estimated wait time
        """
        # Check if patient already in queue
        if patient_id in self._queue_cache:
            raise ValueError(f"Patient {patient_id} already in waiting room")
        
        # Get patient details from database
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Add to priority queue (negative priority for max heap behavior)
        self.waiting_queue.enqueue(patient_id, -priority_score)
        
        # Cache patient info
        self._queue_cache[patient_id] = {
            'priority': priority_score,
            'added_at': datetime.now(),
            'patient_name': patient.name,
            'esi_level': patient.esi_level,
            'created_at': patient.created_at
        }
        
        position = self._get_position_in_queue(patient_id)
        
        return {
            'status': 'added',
            'patient_id': patient_id,
            'patient_name': patient.name,
            'priority_score': priority_score,
            'position_in_queue': position,
            'total_waiting': self.waiting_queue.size(),
            'estimated_wait_minutes': self.get_estimated_wait_time(patient_id)
        }
    
    def get_next_patient(self) -> Optional[str]:
        """
        Dequeue the next patient (highest priority).
        Returns patient_id or None if queue is empty.
        """
        if self.waiting_queue.is_empty():
            return None
        
        patient_id = self.waiting_queue.dequeue()
        
        # Remove from cache
        if patient_id in self._queue_cache:
            del self._queue_cache[patient_id]
        
        return patient_id
    
    def peek_next_patient(self) -> Optional[str]:
        """View next patient without removing from queue"""
        if self.waiting_queue.is_empty():
            return None
        return self.waiting_queue.peek()
    
    def get_waiting_count(self) -> int:
        """Get number of patients in waiting room"""
        return self.waiting_queue.size()
    
    def get_queue_status(self, db: Session) -> Dict:
        """
        Get comprehensive status of waiting room queue.
        
        Args:
            db: Database session
        
        Returns:
            Dict with total waiting, patient list with details, and next patient
        """
        if self.waiting_queue.is_empty():
            return {
                'total_waiting': 0,
                'patients': [],
                'avg_wait_time': 0
            }
        
        # Get all patients in queue with their details
        patients_info = []
        for patient_id, cached_info in self._queue_cache.items():
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                wait_time = (datetime.now() - cached_info['added_at']).total_seconds() / 60
                patients_info.append({
                    'patient_id': patient_id,
                    'name': patient.name,
                    'esi_level': patient.esi_level,
                    'priority_score': cached_info['priority'],
                    'position': self._get_position_in_queue(patient_id),
                    'wait_time_minutes': int(wait_time),
                    'estimated_wait_minutes': self.get_estimated_wait_time(patient_id)
                })
        
        # Sort by position
        patients_info.sort(key=lambda x: x['position'])
        
        avg_wait = sum(p['wait_time_minutes'] for p in patients_info) / len(patients_info) if patients_info else 0
        
        return {
            'total_waiting': self.waiting_queue.size(),
            'patients': patients_info,
            'avg_wait_time': int(avg_wait),
            'next_patient': patients_info[0] if patients_info else None
        }
    
    def remove_patient(self, patient_id: str) -> bool:
        """
        Remove patient from waiting room (if they're admitted or leave).
        Returns True if removed, False if not found.
        """
        if patient_id not in self._queue_cache:
            return False
        
        # Note: Can't efficiently remove from middle of priority queue
        # In production, would use a more sophisticated data structure
        # For now, just remove from cache and skip when dequeued
        del self._queue_cache[patient_id]
        return True
    
    def update_priority(self, patient_id: str, new_priority: float) -> bool:
        """
        Update priority of patient in queue.
        Returns True if updated, False if not found.
        """
        if patient_id not in self._queue_cache:
            return False
        
        # Update cache
        self._queue_cache[patient_id]['priority'] = new_priority
        
        # Note: Priority queue doesn't support efficient priority updates
        # In production, would rebuild queue or use more sophisticated structure
        return True
    
    def clear_queue(self):
        """Clear all patients from waiting room queue"""
        self.waiting_queue = PriorityQueue()
        self._queue_cache = {}
    
    def get_estimated_wait_time(self, patient_id: str, avg_treatment_time: int = 30) -> Optional[int]:
        """
        Estimate wait time for patient based on position in queue.
        
        Args:
            patient_id: Patient identifier
            avg_treatment_time: Average treatment time in minutes (default: 30)
        
        Returns:
            Estimated wait time in minutes, or None if patient not in queue
        """
        if patient_id not in self._queue_cache:
            return None
        
        position = self._get_position_in_queue(patient_id)
        # Each patient ahead takes avg_treatment_time
        return (position - 1) * avg_treatment_time
    
    def _get_position_in_queue(self, patient_id: str) -> int:
        """
        Get position of patient in queue (1-indexed).
        1 = next to be treated, 2 = second in line, etc.
        """
        if patient_id not in self._queue_cache:
            return -1
        
        # Sort all patients by priority (descending)
        sorted_patients = sorted(
            self._queue_cache.items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        )
        
        for i, (pid, _) in enumerate(sorted_patients, 1):
            if pid == patient_id:
                return i
        
        return -1
