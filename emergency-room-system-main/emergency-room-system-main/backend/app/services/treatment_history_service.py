# backend/app/services/treatment_history_service.py
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import uuid

from app.core.stack import Stack
from app.models.treatment import TreatmentHistory


class TreatmentHistoryService:
    def __init__(self):
        # Keep in-memory stacks for quick undo operations
        # Stack contains treatment IDs for quick access
        self.history_stacks: Dict[str, Stack] = {}

    def add_action(self, patient_id: str, action_input: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Add a treatment action to database and stack."""
        # Create unique ID for this action
        action_id = f"TRT{str(uuid.uuid4())[:12].upper()}"
        
        # Save to database
        treatment = TreatmentHistory(
            id=action_id,
            patient_id=patient_id,
            action_type=action_input.get("action_type"),
            performed_by=action_input.get("performed_by"),
            details=action_input.get("details", {}),
            notes=action_input.get("notes"),
            is_undone="false"
        )
        
        db.add(treatment)
        db.commit()
        db.refresh(treatment)
        
        # Add to in-memory stack for quick undo
        if patient_id not in self.history_stacks:
            self.history_stacks[patient_id] = Stack()
        self.history_stacks[patient_id].push(action_id)
        
        return treatment.to_dict()

    def undo_last_action(self, patient_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Undo (mark as undone) the last treatment action for a patient."""
        if patient_id not in self.history_stacks or self.history_stacks[patient_id].is_empty():
            # Try to rebuild stack from database
            self._rebuild_stack(patient_id, db)
            
            if patient_id not in self.history_stacks or self.history_stacks[patient_id].is_empty():
                return None
        
        # Get last action ID from stack
        action_id = self.history_stacks[patient_id].pop()
        
        # Mark as undone in database
        treatment = db.query(TreatmentHistory).filter(TreatmentHistory.id == action_id).first()
        if treatment:
            treatment.is_undone = "true"
            treatment.undone_at = datetime.utcnow()
            db.commit()
            return treatment.to_dict()
        
        return None

    def peek_last_action(self, patient_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """View the last treatment action without removing it."""
        if patient_id not in self.history_stacks or self.history_stacks[patient_id].is_empty():
            self._rebuild_stack(patient_id, db)
            
            if patient_id not in self.history_stacks or self.history_stacks[patient_id].is_empty():
                return None
        
        action_id = self.history_stacks[patient_id].peek()
        treatment = db.query(TreatmentHistory).filter(TreatmentHistory.id == action_id).first()
        
        return treatment.to_dict() if treatment else None

    def get_history_size(self, patient_id: str, db: Session) -> int:
        """Get the number of active (not undone) actions in patient's history."""
        count = db.query(TreatmentHistory).filter(
            TreatmentHistory.patient_id == patient_id,
            TreatmentHistory.is_undone == "false"
        ).count()
        return count

    def get_full_history(self, patient_id: str, db: Session, include_undone: bool = False) -> List[Dict[str, Any]]:
        """Get complete treatment history for a patient."""
        query = db.query(TreatmentHistory).filter(TreatmentHistory.patient_id == patient_id)
        
        if not include_undone:
            query = query.filter(TreatmentHistory.is_undone == "false")
        
        treatments = query.order_by(TreatmentHistory.timestamp.desc()).all()
        return [t.to_dict() for t in treatments]

    def clear_history(self, patient_id: str, db: Session) -> bool:
        """Clear stack for a patient (database records remain for audit)."""
        if patient_id in self.history_stacks:
            self.history_stacks[patient_id].clear()
            return True
        return False

    def _rebuild_stack(self, patient_id: str, db: Session):
        """Rebuild in-memory stack from database records."""
        treatments = db.query(TreatmentHistory).filter(
            TreatmentHistory.patient_id == patient_id,
            TreatmentHistory.is_undone == "false"
        ).order_by(TreatmentHistory.timestamp.asc()).all()
        
        if treatments:
            self.history_stacks[patient_id] = Stack()
            for t in treatments:
                self.history_stacks[patient_id].push(t.id)

