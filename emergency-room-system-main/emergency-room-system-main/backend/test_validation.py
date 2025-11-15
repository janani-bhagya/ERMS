#!/usr/bin/env python3
"""
Quick test script to verify resource allocation validation
Tests the start_treatment endpoint validation logic
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_start_treatment_validation():
    """Test that start_treatment requires resource allocation"""
    
    print("=" * 70)
    print("Testing Start Treatment Validation")
    print("=" * 70)
    
    # Test 1: Try to start treatment without allocation (should FAIL)
    print("\n📋 Test 1: Start treatment without allocation (should fail)")
    print("-" * 70)
    
    patient_id = "P20251020002"  # Emma Thompson - waiting patient
    
    try:
        response = requests.put(f"{BASE_URL}/patients/{patient_id}/start-treatment")
        if response.status_code == 400:
            print("✅ PASS: Got expected 400 error")
            print(f"Error message: {response.json()['detail'][:100]}...")
        else:
            print(f"❌ FAIL: Expected 400, got {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Allocate resources
    print("\n📋 Test 2: Allocate resources (room + providers)")
    print("-" * 70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/resources/allocate",
            params={
                "patient_id": patient_id,
                "room_id": "ROOM002"
            },
            json=["DR002", "NR002"]
        )
        if response.status_code == 200:
            print("✅ PASS: Resources allocated successfully")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Try to start treatment WITH allocation (should SUCCEED)
    print("\n📋 Test 3: Start treatment with allocation (should succeed)")
    print("-" * 70)
    
    try:
        response = requests.put(f"{BASE_URL}/patients/{patient_id}/start-treatment")
        if response.status_code == 200:
            print("✅ PASS: Treatment started successfully")
            data = response.json()
            print(f"Room: {data.get('room', 'N/A')}")
            print(f"Providers: {', '.join(data.get('providers', []))}")
            print(f"Summary: {data.get('summary', 'N/A')}")
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    print("\n⚠️  Make sure backend is running: uvicorn app.main:fastapi_app --reload")
    print("⚠️  Make sure database is seeded: ./scripts/reset_and_seed.sh\n")
    
    input("Press Enter to start tests...")
    
    test_start_treatment_validation()
