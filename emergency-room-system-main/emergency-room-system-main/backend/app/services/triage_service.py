# backend/app/services/triage_service.py
from app.core.heap import MaxHeap
from app.schemas.patient import Patient, ESILevel
import time


class TriageService:
    def __init__(self):
        self.heap = MaxHeap()
    
    def calculate_priority_score(self, esi_level: ESILevel, waiting_time: int, vital_signs: dict) -> float:
        """Calculate priority score based on ESI, waiting time, and vital signs"""
        base_score = {
            ESILevel.LEVEL_1: 100,
            ESILevel.LEVEL_2: 80,
            ESILevel.LEVEL_3: 60,
            ESILevel.LEVEL_4: 40,
            ESILevel.LEVEL_5: 20
        }[esi_level]
        
        # Adjust based on waiting time (increases priority over time)
        time_adjustment = min(waiting_time * 0.1, 20)  # Max 20 point adjustment
        
        # Adjust based on vital signs abnormalities
        vital_adjustment = self._calculate_vital_adjustment(vital_signs)
        
        return base_score + time_adjustment + vital_adjustment
    
    def _calculate_vital_adjustment(self, vital_signs: dict) -> float:
        """Calculate adjustment based on vital sign abnormalities"""
        adjustment = 0
        
        # Simple heuristic - in production, use proper medical scoring systems
        if 'heart_rate' in vital_signs:
            hr = vital_signs['heart_rate']
            if hr < 50 or hr > 120:
                adjustment += 10
        
        if 'blood_pressure' in vital_signs:
            bp = vital_signs['blood_pressure']
            if isinstance(bp, str) and '/' in bp:
                systolic, diastolic = map(int, bp.split('/'))
                if systolic < 90 or systolic > 180:
                    adjustment += 10
        
        if 'oxygen_saturation' in vital_signs:
            spo2 = vital_signs['oxygen_saturation']
            if spo2 < 92:
                adjustment += 15
        
        return adjustment
    
    def add_patient(self, patient_data: dict) -> str:
        """Add new patient to triage system. Expects patient_data to include an 'id' key if an external
        patient id is used (e.g. created by PatientService). Returns the patient_id used."""
        patient_id = patient_data.get('id')
        if not patient_id:
            # fallback to an internal id if none provided
            # internal ids start with P
            # note: this path is kept for backward compatibility
            self_local_counter = getattr(self, '_local_counter', 0) + 1
            setattr(self, '_local_counter', self_local_counter)
            patient_id = f"P{self_local_counter:06d}"
        
        waiting_time = patient_data.get('waiting_time', 0)
        priority_score = self.calculate_priority_score(
            patient_data['esi_level'],
            waiting_time,
            patient_data['vital_signs']
        )
        
        clinical_data = {
            'patient_data': patient_data,
            'waiting_time': waiting_time,
            'timestamp': time.time()
        }
        
        self.heap.push(priority_score, patient_id, clinical_data)
        return patient_id
    
    def get_next_patient(self):
        """Get next highest priority patient"""
        return self.heap.pop()
    
    def update_patient_priority(self, patient_id: str, new_data: dict):
        """Update patient priority based on new information"""
        # In production, we'd look up the patient and recalculate
        # For now, this is a simplified version
        pass
    