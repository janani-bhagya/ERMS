# backend/app/services/resource_service.py
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.core.graph import Graph
from app.core.queue import PriorityQueue
from app.models.resource import Room, Equipment, Provider


class ResourceService:
    def __init__(self):
        # Graph for resource dependencies and optimization
        self.resource_graph = Graph()
        
        # Priority queue for lab test scheduling
        self.lab_queue = PriorityQueue()

    def _sync_graph_from_db(self, db: Session):
        """Sync resource graph with database state"""
        # Add all resources as vertices
        rooms = db.query(Room).all()
        equipment = db.query(Equipment).all()
        providers = db.query(Provider).all()
        
        for room in rooms:
            self.resource_graph.add_vertex(room.id)
        for eq in equipment:
            self.resource_graph.add_vertex(eq.id)
        for prov in providers:
            self.resource_graph.add_vertex(prov.id)

    # Lab Test Queue Management
    def schedule_lab_test(self, patient_id: str, test_type: str, priority: int, requested_by: str, notes: Optional[str] = None):
        """Add lab test request to priority queue"""
        test_request = {
            "patient_id": patient_id,
            "test_type": test_type,
            "priority": priority,
            "requested_by": requested_by,
            "notes": notes,
        }
        self.lab_queue.enqueue(test_request, priority)
        return test_request

    def get_next_lab_test(self) -> Optional[Dict[str, Any]]:
        """Get next highest priority lab test from queue"""
        return self.lab_queue.dequeue()

    def peek_next_lab_test(self) -> Optional[Dict[str, Any]]:
        """View next lab test without removing it"""
        return self.lab_queue.peek()

    def get_lab_queue_size(self) -> int:
        """Get number of pending lab tests"""
        return self.lab_queue.size()

    # Room Management
    def get_room(self, room_id: str, db: Session) -> Optional[Dict[str, Any]]:
        room = db.query(Room).filter(Room.id == room_id).first()
        return room.to_dict() if room else None

    def get_available_rooms(self, db: Session, room_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available rooms, optionally filtered by type"""
        query = db.query(Room).filter(Room.status == "available")
        
        if room_type:
            query = query.filter(Room.room_type == room_type)
        
        rooms = query.all()
        return [r.to_dict() for r in rooms]

    def assign_room(self, room_id: str, patient_id: str, db: Session) -> bool:
        """Assign a room to a patient"""
        room = db.query(Room).filter(Room.id == room_id).first()
        
        if not room or room.status != "available":
            return False
        
        room.status = "occupied"
        room.current_patient_id = patient_id
        db.commit()
        
        # Add edge in graph for tracking
        self.resource_graph.add_edge(patient_id, room_id, weight=1)
        return True

    def release_room(self, room_id: str, db: Session) -> bool:
        """Release a room (mark as cleaning)"""
        room = db.query(Room).filter(Room.id == room_id).first()
        
        if not room:
            return False
        
        room.status = "cleaning"
        room.current_patient_id = None
        db.commit()
        return True

    # Equipment Management
    def get_equipment(self, equipment_id: str, db: Session) -> Optional[Dict[str, Any]]:
        eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
        return eq.to_dict() if eq else None

    def get_available_equipment(self, db: Session, equipment_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available equipment, optionally filtered by type"""
        query = db.query(Equipment).filter(Equipment.status == "available")
        
        if equipment_type:
            query = query.filter(Equipment.equipment_type == equipment_type)
        
        equipment = query.all()
        return [e.to_dict() for e in equipment]

    def assign_equipment(self, equipment_id: str, location: str, db: Session) -> bool:
        """Assign equipment to a location (room)"""
        eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
        
        if not eq or eq.status != "available":
            return False
        
        eq.status = "in_use"
        eq.location = location
        db.commit()
        
        # Add edge in graph
        self.resource_graph.add_edge(equipment_id, location, weight=1)
        return True

    # Provider Management
    def get_provider(self, provider_id: str, db: Session) -> Optional[Dict[str, Any]]:
        prov = db.query(Provider).filter(Provider.id == provider_id).first()
        return prov.to_dict() if prov else None

    def get_available_providers(self, db: Session, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available providers, optionally filtered by role"""
        query = db.query(Provider).filter(Provider.is_available == "true")
        
        if role:
            query = query.filter(Provider.role == role)
        
        providers = query.all()
        return [p.to_dict() for p in providers]

    def assign_provider(self, provider_id: str, patient_id: str, db: Session) -> bool:
        """Assign a provider to a patient"""
        prov = db.query(Provider).filter(Provider.id == provider_id).first()
        
        if not prov or prov.is_available != "true":
            return False
        
        current_patients = prov.current_patient_ids or []
        if patient_id not in current_patients:
            current_patients.append(patient_id)
        prov.current_patient_ids = current_patients
        
        # Mark unavailable if at capacity (max 3 patients per provider)
        if len(current_patients) >= 3:
            prov.is_available = "false"
        
        db.commit()
        
        # Add edge in graph
        self.resource_graph.add_edge(provider_id, patient_id, weight=1)
        return True

    # Graph-based Resource Optimization
    def find_resource_bottlenecks(self, db: Session) -> List[str]:
        """Identify resource nodes with highest connections (bottlenecks)"""
        self._sync_graph_from_db(db)
        return self.resource_graph.find_bottlenecks()

    def optimize_staff_path(self, staff_id: str, target_room_id: str) -> List[str]:
        """Find optimal path for staff to reach a room"""
        try:
            return self.resource_graph.shortest_path(staff_id, target_room_id)
        except:
            return []

    def get_resource_graph_summary(self, db: Session) -> Dict[str, Any]:
        """Get summary of resource graph state"""
        self._sync_graph_from_db(db)
        
        vertices = self.resource_graph.get_vertices()
        bottlenecks = self.resource_graph.find_bottlenecks()
        
        # Get counts from database
        room_count = db.query(Room).count()
        equipment_count = db.query(Equipment).count()
        provider_count = db.query(Provider).count()
        
        return {
            "total_resources": len(vertices),
            "bottlenecks": bottlenecks,
            "resource_types": {
                "rooms": room_count,
                "equipment": equipment_count,
                "providers": provider_count,
            }
        }

