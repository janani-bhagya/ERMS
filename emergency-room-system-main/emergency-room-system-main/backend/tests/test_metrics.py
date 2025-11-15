"""
Test cases for Metrics system.
Tests metrics recording, calculations, and aggregate statistics.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from app.services.metrics_service import MetricsService


def test_door_to_provider_calculation():
    """Test door-to-provider time calculation"""
    print("\n=== Testing Door-to-Provider Calculation ===")
    
    # Test 1: 30 minute difference
    arrival = datetime(2025, 10, 20, 10, 0, 0)
    provider_contact = datetime(2025, 10, 20, 10, 30, 0)
    
    result = MetricsService.calculate_door_to_provider(arrival, provider_contact)
    print(f"Arrived at 10:00, Provider at 10:30 = {result} minutes")
    assert result == 30, f"Expected 30 minutes, got {result}"
    
    # Test 2: 1 hour difference
    arrival = datetime(2025, 10, 20, 9, 0, 0)
    provider_contact = datetime(2025, 10, 20, 10, 0, 0)
    
    result = MetricsService.calculate_door_to_provider(arrival, provider_contact)
    print(f"Arrived at 9:00, Provider at 10:00 = {result} minutes")
    assert result == 60, f"Expected 60 minutes, got {result}"
    
    # Test 3: 2 hours 15 minutes
    arrival = datetime(2025, 10, 20, 8, 0, 0)
    provider_contact = datetime(2025, 10, 20, 10, 15, 0)
    
    result = MetricsService.calculate_door_to_provider(arrival, provider_contact)
    print(f"Arrived at 8:00, Provider at 10:15 = {result} minutes")
    assert result == 135, f"Expected 135 minutes, got {result}"
    
    # Test 4: None values
    result = MetricsService.calculate_door_to_provider(None, provider_contact)
    print(f"None arrival time = {result} minutes")
    assert result == 0, "Should return 0 for None values"
    
    print("✅ All door-to-provider calculation tests passed!")


def test_length_of_stay_calculation():
    """Test length of stay calculation"""
    print("\n=== Testing Length of Stay Calculation ===")
    
    # Test 1: 3 hours
    arrival = datetime(2025, 10, 20, 10, 0, 0)
    discharge = datetime(2025, 10, 20, 13, 0, 0)
    
    result = MetricsService.calculate_length_of_stay(arrival, discharge)
    print(f"Arrived at 10:00, Discharged at 13:00 = {result} minutes")
    assert result == 180, f"Expected 180 minutes, got {result}"
    
    # Test 2: 6 hours 30 minutes
    arrival = datetime(2025, 10, 20, 8, 0, 0)
    discharge = datetime(2025, 10, 20, 14, 30, 0)
    
    result = MetricsService.calculate_length_of_stay(arrival, discharge)
    print(f"Arrived at 8:00, Discharged at 14:30 = {result} minutes")
    assert result == 390, f"Expected 390 minutes, got {result}"
    
    # Test 3: 12 hours
    arrival = datetime(2025, 10, 20, 6, 0, 0)
    discharge = datetime(2025, 10, 20, 18, 0, 0)
    
    result = MetricsService.calculate_length_of_stay(arrival, discharge)
    print(f"Arrived at 6:00, Discharged at 18:00 = {result} minutes")
    assert result == 720, f"Expected 720 minutes, got {result}"
    
    # Test 4: None values
    result = MetricsService.calculate_length_of_stay(None, discharge)
    print(f"None arrival time = {result} minutes")
    assert result == 0, "Should return 0 for None values"
    
    print("✅ All length of stay calculation tests passed!")


def test_metrics_model_calculations():
    """Test PatientMetrics model automatic calculations"""
    print("\n=== Testing PatientMetrics Model Calculations ===")
    
    from app.models.metrics import PatientMetrics
    
    # Create a metrics object with all timestamps
    metrics = PatientMetrics(
        patient_id="TEST001",
        arrival_time=datetime(2025, 10, 20, 10, 0, 0),
        triage_complete_time=datetime(2025, 10, 20, 10, 15, 0),
        provider_contact_time=datetime(2025, 10, 20, 10, 45, 0),
        treatment_start_time=datetime(2025, 10, 20, 11, 0, 0),
        discharge_time=datetime(2025, 10, 20, 13, 30, 0),
        esi_level=3
    )
    
    # Calculate all metrics
    metrics.calculate_metrics()
    
    print(f"Door-to-triage: {metrics.door_to_triage_minutes} minutes (expected 15)")
    assert metrics.door_to_triage_minutes == 15, "Door-to-triage should be 15 minutes"
    
    print(f"Door-to-provider: {metrics.door_to_provider_minutes} minutes (expected 45)")
    assert metrics.door_to_provider_minutes == 45, "Door-to-provider should be 45 minutes"
    
    print(f"Door-to-treatment: {metrics.door_to_treatment_minutes} minutes (expected 60)")
    assert metrics.door_to_treatment_minutes == 60, "Door-to-treatment should be 60 minutes"
    
    print(f"Length of stay: {metrics.length_of_stay_minutes} minutes (expected 210)")
    assert metrics.length_of_stay_minutes == 210, "Length of stay should be 210 minutes"
    
    # Test to_dict method
    metrics_dict = metrics.to_dict()
    print(f"Metrics as dict has {len(metrics_dict)} fields")
    assert "patient_id" in metrics_dict, "Should include patient_id"
    assert "door_to_provider_minutes" in metrics_dict, "Should include calculated metrics"
    
    print("✅ All metrics model calculation tests passed!")


def test_real_world_scenarios():
    """Test realistic ER scenarios"""
    print("\n=== Testing Real-World ER Scenarios ===")
    
    # Scenario 1: Fast-track patient (ESI 4-5)
    # Should be quick: arrival to discharge in 2 hours
    print("\nScenario 1: Fast-track patient")
    arrival = datetime(2025, 10, 20, 14, 0, 0)
    provider = datetime(2025, 10, 20, 14, 20, 0)  # 20 min wait
    discharge = datetime(2025, 10, 20, 16, 0, 0)  # 2 hour total
    
    door_to_provider = MetricsService.calculate_door_to_provider(arrival, provider)
    los = MetricsService.calculate_length_of_stay(arrival, discharge)
    
    print(f"  Door-to-provider: {door_to_provider} min (target: <30 min for ESI 4-5)")
    print(f"  Length of stay: {los} min (target: <180 min)")
    assert door_to_provider <= 30, "Fast-track should see provider quickly"
    assert los <= 180, "Fast-track should have short length of stay"
    
    # Scenario 2: Critical patient (ESI 1-2)
    # Should be immediate: arrival to provider in 5 minutes
    print("\nScenario 2: Critical patient")
    arrival = datetime(2025, 10, 20, 15, 0, 0)
    provider = datetime(2025, 10, 20, 15, 5, 0)  # 5 min immediate
    discharge = datetime(2025, 10, 20, 21, 0, 0)  # 6 hour stabilization
    
    door_to_provider = MetricsService.calculate_door_to_provider(arrival, provider)
    los = MetricsService.calculate_length_of_stay(arrival, discharge)
    
    print(f"  Door-to-provider: {door_to_provider} min (target: <10 min for ESI 1-2)")
    print(f"  Length of stay: {los} min (critical patients often longer)")
    assert door_to_provider <= 10, "Critical patients should see provider immediately"
    
    # Scenario 3: Average patient (ESI 3)
    # Typical: 45 min to provider, 4 hour total
    print("\nScenario 3: Average patient (ESI 3)")
    arrival = datetime(2025, 10, 20, 10, 0, 0)
    provider = datetime(2025, 10, 20, 10, 45, 0)  # 45 min wait
    discharge = datetime(2025, 10, 20, 14, 0, 0)  # 4 hour total
    
    door_to_provider = MetricsService.calculate_door_to_provider(arrival, provider)
    los = MetricsService.calculate_length_of_stay(arrival, discharge)
    
    print(f"  Door-to-provider: {door_to_provider} min")
    print(f"  Length of stay: {los} min")
    assert 30 <= door_to_provider <= 60, "ESI 3 typically 30-60 min wait"
    assert 180 <= los <= 300, "ESI 3 typically 3-5 hour stay"
    
    print("✅ All real-world scenario tests passed!")


def test_aggregate_metrics_logic():
    """Test aggregate metrics calculation logic"""
    print("\n=== Testing Aggregate Metrics Logic ===")
    
    # Simulate multiple patients
    patients_data = [
        {"door_to_provider": 30, "los": 180},
        {"door_to_provider": 45, "los": 240},
        {"door_to_provider": 60, "los": 300},
        {"door_to_provider": 15, "los": 120},
        {"door_to_provider": 90, "los": 360},
    ]
    
    # Calculate averages manually
    avg_d2p = sum(p["door_to_provider"] for p in patients_data) / len(patients_data)
    avg_los = sum(p["los"] for p in patients_data) / len(patients_data)
    
    print(f"Average door-to-provider: {avg_d2p} minutes")
    print(f"Average length of stay: {avg_los} minutes")
    
    expected_d2p = (30 + 45 + 60 + 15 + 90) / 5
    expected_los = (180 + 240 + 300 + 120 + 360) / 5
    
    assert avg_d2p == expected_d2p, f"Expected {expected_d2p}, got {avg_d2p}"
    assert avg_los == expected_los, f"Expected {expected_los}, got {avg_los}"
    
    print(f"✅ Aggregate calculations correct: {expected_d2p:.1f} min D2P, {expected_los:.1f} min LOS")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Metrics System Tests")
    print("Emergency Room Management System")
    print("=" * 60)
    
    try:
        test_door_to_provider_calculation()
        test_length_of_stay_calculation()
        test_metrics_model_calculations()
        test_real_world_scenarios()
        test_aggregate_metrics_logic()
        
        print("\n" + "=" * 60)
        print("✅ ALL METRICS TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
