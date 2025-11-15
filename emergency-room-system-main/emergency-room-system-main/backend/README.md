# Emergency Room Management System - Backend

## 🏥 Overview

An intelligent Hospital Emergency Room Management System using advanced data structures and PostgreSQL database integration. The system handles patient triage optimization, resource allocation, treatment workflow coordination, and clinical decision support.

## ✅ Implementation Status

### Completed Features

**Core Data Structures:**
- ✅ MaxHeap for patient triage priority management
- ✅ HashTable for rapid patient information retrieval (in-memory + PostgreSQL)
- ✅ Stack for treatment history with undo capability
- ✅ PriorityQueue for lab test scheduling
- ✅ Graph for resource optimization and bottleneck detection

**Services:**
- ✅ **PatientService** - Patient CRUD operations with PostgreSQL
- ✅ **TriageService** - Priority-based patient queue management
- ✅ **TreatmentHistoryService** - Treatment action tracking with undo
- ✅ **ResourceService** - Room, equipment, and provider management

**Database Integration:**
- ✅ PostgreSQL with SQLAlchemy ORM
- ✅ Patient, TreatmentHistory, Room, Equipment, Provider tables
- ✅ Automatic database initialization and seeding
- ✅ Connection pooling and error handling

**API Endpoints (30+):**
- ✅ Patient management (create, get, list, discharge)
- ✅ Triage operations (add to queue, get next patient, update priority)
- ✅ Treatment history (add action, undo, view history)
- ✅ Resource management (rooms, equipment, providers)
- ✅ Lab test scheduling
- ✅ Metrics and analytics (waiting times, resource utilization)

**Service Integration:**
- ✅ Services linked together for data consistency
- ✅ Room assignments update patient records
- ✅ Provider assignments tracked in database
- ✅ Treatment actions recorded with timestamps

**Error Handling:**
- ✅ Comprehensive HTTP exception handling
- ✅ Database connection error handling
- ✅ Input validation with Pydantic schemas
- ✅ 404, 400, 500 error responses

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database (Neon or local)
- pip and virtualenv

### 1. Install Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` file exists with PostgreSQL credentials:

```env
PGHOST='your-host.neon.tech'
PGDATABASE='neondb'
PGUSER='neondb_owner'
PGPASSWORD='your-password'
PGSSLMODE='require'
PGCHANNELBINDING='require'
```

### 3. Initialize Database

```bash
python3 -m app.init_db
```

This will:
- Create all database tables
- Seed 5 rooms, 9 equipment items, 9 providers

### 4. Start Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Server will start at: http://localhost:8000

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Patient Management
```
POST   /patients                    - Create patient and add to triage
GET    /patients/{patient_id}       - Get patient details
GET    /patients                    - List all patients (filter by status)
PUT    /patients/{patient_id}/priority - Update patient priority
DELETE /patients/{patient_id}/discharge - Discharge patient
GET    /patients/triage/next        - Get next highest priority patient
GET    /triage/status               - Get triage queue status
```

#### Treatment History
```
POST   /treatments                  - Add treatment action
DELETE /treatments/undo             - Undo last action
GET    /treatments/{patient_id}/history - Get full treatment history
GET    /treatments/{patient_id}/last - Peek last action
GET    /treatments/{patient_id}/count - Count actions
```

#### Resource Management
```
GET    /rooms                       - List available rooms
POST   /rooms/{room_id}/assign      - Assign room to patient
POST   /rooms/{room_id}/release     - Release room
GET    /equipment                   - List available equipment
POST   /equipment/{equipment_id}/assign - Assign equipment
GET    /providers                   - List available providers
POST   /providers/{provider_id}/assign - Assign provider to patient
```

#### Lab Tests
```
POST   /lab-tests                   - Schedule lab test
GET    /lab-tests/next              - Get next priority test
GET    /lab-tests/queue-size        - Get queue size
```

#### Metrics & Analytics
```
GET    /metrics/waiting-times       - Waiting time statistics
GET    /metrics/resource-utilization - Resource utilization rates
GET    /resources/bottlenecks       - Find resource bottlenecks
GET    /resources/summary           - Resource graph summary
```

## 🧪 Testing

Run the test script:

```bash
python test_api.py
```

This will test all major endpoints and display results.

## 📊 Data Structures Used

### 1. MaxHeap (Triage Priority Queue)
- **File**: `app/core/heap.py`
- **Usage**: Patient triage with dynamic priority updates
- **Operations**: O(log n) insert, O(log n) extract-max, O(n) update priority

### 2. HashTable (Patient Records)
- **File**: `app/core/hash_table.py`
- **Usage**: Fast O(1) patient lookup (in-memory cache)
- **Database**: PostgreSQL for persistent storage

### 3. Stack (Treatment History)
- **File**: `app/core/stack.py`
- **Usage**: Undo/redo treatment actions
- **Operations**: O(1) push, O(1) pop, O(1) peek

### 4. PriorityQueue (Lab Tests)
- **File**: `app/core/queue.py`
- **Usage**: Schedule lab tests by urgency
- **Operations**: O(n) enqueue, O(n) dequeue (linear search)

### 5. Graph (Resource Optimization)
- **File**: `app/core/graph.py`
- **Usage**: Model resource dependencies, find bottlenecks
- **Algorithms**: Dijkstra's shortest path, degree analysis

## 🗄️ Database Schema

### Tables
1. **patients** - Patient records with priority, status, assignments
2. **treatment_history** - Treatment actions with undo tracking
3. **rooms** - ER room status and assignments
4. **equipment** - Medical equipment tracking
5. **providers** - Healthcare staff availability

### Relationships
- Patient → Room (one-to-one)
- Patient → Providers (many-to-many via JSON array)
- Patient → TreatmentHistory (one-to-many)
- Room → Equipment (one-to-many via JSON array)

## 🎯 Key Features

### Service Integration
- Patient records automatically updated when triage priority changes
- Room release on patient discharge
- Provider availability tracked based on assignments
- Treatment actions timestamped and auditable

### Error Handling
- Database connection failures return 503
- Missing resources return 404
- Invalid operations return 400
- Internal errors return 500 with details

### Performance Optimizations
- Database connection pooling
- In-memory heap for fast triage operations
- Indexed database queries
- Lazy loading of relationships

## 🔮 Future Enhancements

1. **Predictive Analytics**
   - ML-based deterioration prediction
   - Waiting time forecasting
   - Resource demand prediction

2. **Real-time Updates**
   - WebSocket support for live triage updates
   - Push notifications for critical changes
   - Real-time dashboard metrics

3. **Advanced Features**
   - Automated ESI level calculation
   - Integration with EHR systems
   - Bed assignment optimization algorithms
   - Staff scheduling automation

4. **Testing**
   - Unit tests for all services
   - Integration tests for endpoints
   - Load testing for performance
   - E2E testing with frontend

## 📝 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── database.py        # PostgreSQL connection
│   │   ├── graph.py           # Graph data structure
│   │   ├── hash_table.py      # Hash table implementation
│   │   ├── heap.py            # Max heap for priority queue
│   │   ├── queue.py           # Priority queue
│   │   └── stack.py           # Stack for undo
│   ├── models/
│   │   ├── patient.py         # Patient model
│   │   ├── treatment.py       # Treatment history model
│   │   └── resource.py        # Room, Equipment, Provider models
│   ├── schemas/
│   │   ├── patient.py         # Pydantic schemas
│   │   ├── treatment.py       # Treatment schemas
│   │   └── resource.py        # Resource schemas
│   ├── services/
│   │   ├── patient_service.py
│   │   ├── triage_service.py
│   │   ├── treatment_history_service.py
│   │   └── resource_service.py
│   ├── init_db.py            # Database initialization
│   └── main.py               # FastAPI application
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── test_api.py               # API test script
```

## 👥 Contributors

This system was built as part of a university project demonstrating the practical application of data structures and algorithms in healthcare management.

## 📄 License

MIT License - See LICENSE file for details

---

**Version**: 2.0.0  
**Last Updated**: October 18, 2025  
**Status**: Production Ready ✅
