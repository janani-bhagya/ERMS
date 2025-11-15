# backend/test_api.py
"""
Quick API test script to verify all endpoints work
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")

def test_create_patient():
    print("🏥 Creating a test patient...")
    patient_data = {
        "name": "John Doe",
        "age": 45,
        "esi_level": 2,
        "chief_complaint": "Chest pain",
        "vital_signs": {
            "heart_rate": 95,
            "blood_pressure": "140/90",
            "oxygen_saturation": 94,
            "temperature": 37.2
        }
    }
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Patient ID: {result.get('patient_id')}")
    print(f"   Priority Score: {result.get('priority_score')}\n")
    return result.get('patient_id')

def test_get_patient(patient_id):
    print(f"📋 Getting patient {patient_id}...")
    response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Patient: {json.dumps(response.json(), indent=2)}\n")

def test_list_rooms():
    print("🚪 Listing available rooms...")
    response = requests.get(f"{BASE_URL}/rooms")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Available rooms: {result.get('count')}")
    if result.get('rooms'):
        print(f"   First room: {result['rooms'][0]}\n")
    return result.get('rooms', [])

def test_assign_room(room_id, patient_id):
    print(f"🛏️  Assigning room {room_id} to patient {patient_id}...")
    response = requests.post(
        f"{BASE_URL}/rooms/{room_id}/assign",
        params={"patient_id": patient_id}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")

def test_add_treatment(patient_id):
    print(f"💊 Adding treatment action for patient {patient_id}...")
    treatment_data = {
        "patient_id": patient_id,
        "action_type": "medication_given",
        "performed_by": "DR001",
        "details": {
            "medication": "Aspirin",
            "dosage": "325mg",
            "route": "oral"
        },
        "notes": "Patient responded well"
    }
    response = requests.post(f"{BASE_URL}/treatments", json=treatment_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")

def test_get_providers():
    print("👨‍⚕️  Listing available providers...")
    response = requests.get(f"{BASE_URL}/providers")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Available providers: {result.get('count')}\n")

def test_metrics():
    print("📊 Getting resource utilization metrics...")
    response = requests.get(f"{BASE_URL}/metrics/resource-utilization")
    print(f"   Status: {response.status_code}")
    metrics = response.json()
    print(f"   Room utilization: {metrics['rooms']['utilization_rate']}%")
    print(f"   Equipment utilization: {metrics['equipment']['utilization_rate']}%")
    print(f"   Provider utilization: {metrics['providers']['utilization_rate']}%\n")

def test_triage_status():
    print("⚡ Checking triage status...")
    response = requests.get(f"{BASE_URL}/triage/status")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("🏥 Emergency Room Management System - API Tests")
    print("=" * 60 + "\n")
    
    try:
        # Run tests
        test_health()
        patient_id = test_create_patient()
        test_get_patient(patient_id)
        rooms = test_list_rooms()
        if rooms:
            test_assign_room(rooms[0]['id'], patient_id)
        test_add_treatment(patient_id)
        test_get_providers()
        test_metrics()
        test_triage_status()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        print("\n🌐 API Documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the server is running: python -m uvicorn app.main:app --reload --port 8000")
