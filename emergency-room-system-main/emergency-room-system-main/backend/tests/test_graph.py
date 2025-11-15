"""
Test cases for Graph data structure and algorithms.
Tests BFS, DFS, Dijkstra's shortest path, and bottleneck detection.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.graph import Graph


def test_bfs():
    """Test Breadth-First Search algorithm"""
    print("\n=== Testing BFS ===")
    
    # Create a simple graph
    #     A --- B --- C
    #     |     |     |
    #     D --- E --- F
    
    graph = Graph()
    graph.add_edge('A', 'B', 1)
    graph.add_edge('A', 'D', 1)
    graph.add_edge('B', 'C', 1)
    graph.add_edge('B', 'E', 1)
    graph.add_edge('C', 'F', 1)
    graph.add_edge('D', 'E', 1)
    graph.add_edge('E', 'F', 1)
    
    # Test 1: BFS from A with no depth limit
    result = graph.bfs('A')
    print(f"BFS from A (no limit): {result}")
    assert len(result) == 6, f"Expected 6 vertices, got {len(result)}"
    assert result[0] == ('A', 0), "First vertex should be starting vertex at depth 0"
    
    # Test 2: BFS from A with depth limit 1
    result = graph.bfs('A', max_depth=1)
    print(f"BFS from A (depth 1): {result}")
    vertices_at_depth_1 = [v for v, d in result if d == 1]
    assert set(vertices_at_depth_1) == {'B', 'D'}, "Depth 1 should contain B and D"
    
    # Test 3: BFS from A with depth limit 2
    result = graph.bfs('A', max_depth=2)
    print(f"BFS from A (depth 2): {result}")
    assert len(result) <= 6, "Should not exceed total vertices"
    
    # Test 4: BFS from non-existent vertex
    result = graph.bfs('Z')
    print(f"BFS from non-existent vertex: {result}")
    assert result == [], "Should return empty list for non-existent vertex"
    
    print("✅ All BFS tests passed!")


def test_dfs():
    """Test Depth-First Search algorithm"""
    print("\n=== Testing DFS ===")
    
    # Create a simple graph
    graph = Graph()
    graph.add_edge('A', 'B', 1)
    graph.add_edge('A', 'D', 1)
    graph.add_edge('B', 'C', 1)
    graph.add_edge('B', 'E', 1)
    graph.add_edge('C', 'F', 1)
    graph.add_edge('D', 'E', 1)
    graph.add_edge('E', 'F', 1)
    
    # Test 1: DFS from A (full traversal)
    result = graph.dfs('A')
    print(f"DFS from A (full): {result}")
    assert len(result) == 6, f"Expected 6 vertices, got {len(result)}"
    assert result[0] == 'A', "First vertex should be starting vertex"
    
    # Test 2: DFS from A to F
    result = graph.dfs('A', 'F')
    print(f"DFS from A to F: {result}")
    assert result[0] == 'A', "Should start at A"
    assert result[-1] == 'F' or 'F' in result, "Should reach F"
    
    # Test 3: DFS from non-existent vertex
    result = graph.dfs('Z')
    print(f"DFS from non-existent vertex: {result}")
    assert result == [], "Should return empty list for non-existent vertex"
    
    print("✅ All DFS tests passed!")


def test_dijkstra():
    """Test Dijkstra's shortest path algorithm"""
    print("\n=== Testing Dijkstra's Shortest Path ===")
    
    # Create a weighted graph
    #     A --1-- B --2-- C
    #     |       |       |
    #     3       1       1
    #     |       |       |
    #     D --1-- E --1-- F
    
    graph = Graph()
    graph.add_edge('A', 'B', 1)
    graph.add_edge('A', 'D', 3)
    graph.add_edge('B', 'C', 2)
    graph.add_edge('B', 'E', 1)
    graph.add_edge('C', 'F', 1)
    graph.add_edge('D', 'E', 1)
    graph.add_edge('E', 'F', 1)
    
    # Test 1: Shortest path from A to F
    path = graph.shortest_path('A', 'F')
    print(f"Shortest path from A to F: {path}")
    assert path[0] == 'A' and path[-1] == 'F', "Path should start at A and end at F"
    # Expected path: A -> B -> E -> F (weight: 1 + 1 + 1 = 3)
    assert len(path) == 4, f"Expected path length 4, got {len(path)}"
    
    # Test 2: Shortest path from A to C
    path = graph.shortest_path('A', 'C')
    print(f"Shortest path from A to C: {path}")
    assert path[0] == 'A' and path[-1] == 'C', "Path should start at A and end at C"
    
    # Test 3: Shortest path from D to C
    path = graph.shortest_path('D', 'C')
    print(f"Shortest path from D to C: {path}")
    assert path[0] == 'D' and path[-1] == 'C', "Path should start at D and end at C"
    
    # Test 4: Path to non-existent vertex
    path = graph.shortest_path('A', 'Z')
    print(f"Path to non-existent vertex: {path}")
    assert path == [], "Should return empty list when no path exists"
    
    print("✅ All Dijkstra tests passed!")


def test_bottleneck_detection():
    """Test bottleneck detection (node with most connections)"""
    print("\n=== Testing Bottleneck Detection ===")
    
    # Create a graph where E is the bottleneck (most connections)
    graph = Graph()
    graph.add_edge('A', 'E', 1)
    graph.add_edge('B', 'E', 1)
    graph.add_edge('C', 'E', 1)
    graph.add_edge('D', 'E', 1)
    graph.add_edge('E', 'F', 1)
    graph.add_edge('F', 'G', 1)
    
    # Test 1: Find bottlenecks
    bottlenecks = graph.find_bottlenecks()
    print(f"Bottlenecks (sorted by connections): {bottlenecks}")
    assert len(bottlenecks) > 0, "Should find at least one vertex"
    assert bottlenecks[0][0] == 'E', "E should be the top bottleneck with most connections"
    assert bottlenecks[0][1] == 5, f"E should have 5 connections, got {bottlenecks[0][1]}"
    
    # Test 2: Get node connections for specific node
    connections = graph.get_node_connections('E')
    print(f"Connections for E: {connections}")
    assert connections == 5, f"E should have 5 connections, got {connections}"
    
    # Test 3: Get node connections for node with few connections
    connections = graph.get_node_connections('G')
    print(f"Connections for G: {connections}")
    assert connections == 1, f"G should have 1 connection, got {connections}"
    
    # Test 4: Get node connections for non-existent node
    connections = graph.get_node_connections('Z')
    print(f"Connections for non-existent node: {connections}")
    assert connections == 0, "Should return 0 for non-existent node"
    
    print("✅ All bottleneck detection tests passed!")


def test_real_world_scenario():
    """Test a more realistic ER resource graph scenario"""
    print("\n=== Testing Real-World ER Scenario ===")
    
    # Create a graph representing ER resources
    # Triage -> Waiting Room -> Exam Room -> Lab/Imaging -> Treatment Room -> Discharge
    
    graph = Graph()
    graph.add_edge('Triage', 'WaitingRoom', 5)
    graph.add_edge('WaitingRoom', 'ExamRoom1', 10)
    graph.add_edge('WaitingRoom', 'ExamRoom2', 10)
    graph.add_edge('ExamRoom1', 'Lab', 15)
    graph.add_edge('ExamRoom2', 'Lab', 15)
    graph.add_edge('ExamRoom1', 'Imaging', 20)
    graph.add_edge('ExamRoom2', 'Imaging', 20)
    graph.add_edge('Lab', 'TreatmentRoom', 10)
    graph.add_edge('Imaging', 'TreatmentRoom', 10)
    graph.add_edge('TreatmentRoom', 'Discharge', 5)
    
    # Test 1: Find shortest path from Triage to Discharge
    path = graph.shortest_path('Triage', 'Discharge')
    print(f"Shortest path from Triage to Discharge: {path}")
    assert 'Triage' in path and 'Discharge' in path, "Path should include start and end"
    
    # Test 2: Find resources within 2 steps of Triage
    nearby = graph.bfs('Triage', max_depth=2)
    print(f"Resources within 2 steps of Triage: {nearby}")
    nearby_vertices = [v for v, d in nearby]
    assert 'Triage' in nearby_vertices, "Should include starting point"
    assert 'WaitingRoom' in nearby_vertices, "Should include adjacent resources"
    
    # Test 3: Identify bottlenecks (resources with most connections)
    bottlenecks = graph.find_bottlenecks()
    print(f"Top 3 bottlenecks: {bottlenecks[:3]}")
    # ExamRoom1 and ExamRoom2 should have high connectivity
    top_bottlenecks = [v for v, _ in bottlenecks[:3]]
    assert 'Lab' in top_bottlenecks or 'ExamRoom1' in top_bottlenecks, \
        "Lab or Exam rooms should be bottlenecks"
    
    print("✅ Real-world scenario tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Graph Data Structure Tests")
    print("Emergency Room Management System")
    print("=" * 60)
    
    try:
        test_bfs()
        test_dfs()
        test_dijkstra()
        test_bottleneck_detection()
        test_real_world_scenario()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
