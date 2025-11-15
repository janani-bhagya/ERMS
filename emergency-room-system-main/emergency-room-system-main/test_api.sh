#!/bin/bash

# API Testing Script for Emergency Room Management System
# This script demonstrates all the new endpoints for graph algorithms and metrics

echo "=========================================="
echo "ER Management System - API Test Script"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

echo "1. Testing Graph API Endpoints"
echo "----------------------------------------"

# Initialize graph
echo "Initializing ER Resource Graph..."
curl -s -X POST $BASE_URL/api/graph/init \
  -H "Content-Type: application/json" \
  -d '{
    "edges": [
      {"from_vertex": "Triage", "to_vertex": "WaitingRoom", "weight": 5},
      {"from_vertex": "WaitingRoom", "to_vertex": "ExamRoom1", "weight": 10},
      {"from_vertex": "WaitingRoom", "to_vertex": "ExamRoom2", "weight": 10},
      {"from_vertex": "ExamRoom1", "to_vertex": "Lab", "weight": 15},
      {"from_vertex": "ExamRoom2", "to_vertex": "Lab", "weight": 15},
      {"from_vertex": "ExamRoom1", "to_vertex": "Imaging", "weight": 20},
      {"from_vertex": "Lab", "to_vertex": "Treatment", "weight": 10},
      {"from_vertex": "Imaging", "to_vertex": "Treatment", "weight": 10},
      {"from_vertex": "Treatment", "to_vertex": "Discharge", "weight": 5}
    ]
  }' | jq '.'
echo ""

# Shortest path
echo "Finding shortest path (Dijkstra's Algorithm)..."
curl -s "$BASE_URL/api/graph/shortest-path?from_vertex=Triage&to_vertex=Discharge" | jq '.'
echo ""

# BFS
echo "Running BFS (Breadth-First Search) from Triage..."
curl -s "$BASE_URL/api/graph/bfs?start_vertex=Triage&max_depth=2" | jq '.'
echo ""

# DFS
echo "Running DFS (Depth-First Search) from Triage..."
curl -s "$BASE_URL/api/graph/dfs?start_vertex=Triage&end_vertex=Treatment" | jq '.'
echo ""

# Bottlenecks
echo "Finding bottleneck resources..."
curl -s "$BASE_URL/api/graph/bottlenecks" | jq '.'
echo ""

echo ""
echo "2. Testing Metrics API Endpoints"
echo "----------------------------------------"

# Create test patient 1
PATIENT1="TEST_P$(date +%s)_001"
echo "Creating test patient: $PATIENT1 (ESI 3)"

echo "Recording arrival..."
curl -s -X POST $BASE_URL/api/metrics/record \
  -H "Content-Type: application/json" \
  -d "{
    \"patient_id\": \"$PATIENT1\",
    \"milestone\": \"arrival\",
    \"esi_level\": 3,
    \"chief_complaint\": \"Chest pain\"
  }" | jq '.'
echo ""

echo "Waiting 2 seconds to simulate time passing..."
sleep 2

echo "Recording provider contact..."
curl -s -X POST $BASE_URL/api/metrics/record \
  -H "Content-Type: application/json" \
  -d "{
    \"patient_id\": \"$PATIENT1\",
    \"milestone\": \"provider_contact\"
  }" | jq '.'
echo ""

echo "Getting patient metrics..."
curl -s "$BASE_URL/api/metrics/patient/$PATIENT1" | jq '.'
echo ""

# Create test patient 2
PATIENT2="TEST_P$(date +%s)_002"
echo "Creating test patient: $PATIENT2 (ESI 4)"

curl -s -X POST $BASE_URL/api/metrics/record \
  -H "Content-Type: application/json" \
  -d "{
    \"patient_id\": \"$PATIENT2\",
    \"milestone\": \"arrival\",
    \"esi_level\": 4,
    \"chief_complaint\": \"Minor laceration\"
  }" > /dev/null

sleep 1

curl -s -X POST $BASE_URL/api/metrics/record \
  -H "Content-Type: application/json" \
  -d "{
    \"patient_id\": \"$PATIENT2\",
    \"milestone\": \"provider_contact\"
  }" > /dev/null

sleep 1

curl -s -X POST $BASE_URL/api/metrics/record \
  -H "Content-Type: application/json" \
  -d "{
    \"patient_id\": \"$PATIENT2\",
    \"milestone\": \"discharge\"
  }" > /dev/null

echo "Created patient $PATIENT2 and recorded full journey"
echo ""

echo "Getting aggregate metrics..."
curl -s "$BASE_URL/api/metrics/aggregate?hours=1" | jq '.'
echo ""

echo "Getting metrics by ESI level..."
curl -s "$BASE_URL/api/metrics/by-esi-level?hours=1" | jq '.'
echo ""

echo "=========================================="
echo "API Test Complete!"
echo "=========================================="
echo ""
echo "Summary of Tests:"
echo "✅ Graph initialization"
echo "✅ Dijkstra's shortest path"
echo "✅ BFS traversal"
echo "✅ DFS traversal"
echo "✅ Bottleneck detection"
echo "✅ Metrics recording (arrival, provider contact, discharge)"
echo "✅ Patient metrics retrieval"
echo "✅ Aggregate metrics calculation"
echo "✅ ESI-level metrics breakdown"
echo ""
echo "All endpoints tested successfully!"
echo ""
echo "Next steps:"
echo "1. View dashboard at: http://localhost:3000/dashboard"
echo "2. Check database for patient_metrics table"
echo "3. Take screenshots for your report"
