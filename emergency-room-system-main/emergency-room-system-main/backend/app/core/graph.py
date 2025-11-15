# backend/app/core/graph.py
from typing import Dict, List, Optional, Any

class Graph:
    def __init__(self):
        self.adjacency_list: Dict[Any, List[tuple]] = {}
    
    def add_vertex(self, vertex):
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
    
    def add_edge(self, vertex1, vertex2, weight=1):
        if vertex1 not in self.adjacency_list:
            self.add_vertex(vertex1)
        if vertex2 not in self.adjacency_list:
            self.add_vertex(vertex2)
        
        self.adjacency_list[vertex1].append((vertex2, weight))
        self.adjacency_list[vertex2].append((vertex1, weight))  # Undirected graph
    
    def get_neighbors(self, vertex):
        return self.adjacency_list.get(vertex, [])
    
    def get_vertices(self):
        return list(self.adjacency_list.keys())
    
    def bfs(self, start_vertex, max_depth=None):
        if start_vertex not in self.adjacency_list:
            return []
        
        from collections import deque
        
        visited = set()
        queue = deque([(start_vertex, 0)])
        result = []
        
        while queue:
            current_vertex, depth = queue.popleft()
            
            if current_vertex in visited:
                continue
            
            if max_depth is not None and depth > max_depth:
                continue
            
            visited.add(current_vertex)
            result.append((current_vertex, depth))
            
            for neighbor, _ in self.adjacency_list[current_vertex]:
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        return result
    
    def dfs(self, start_vertex, end_vertex=None):
        if start_vertex not in self.adjacency_list:
            return []
        
        visited = set()
        path = []
        
        def dfs_recursive(vertex):
            visited.add(vertex)
            path.append(vertex)
            
            if end_vertex and vertex == end_vertex:
                return True
            
            for neighbor, _ in self.adjacency_list[vertex]:
                if neighbor not in visited:
                    if dfs_recursive(neighbor):
                        return True
            
            return False
        
        dfs_recursive(start_vertex)
        return path
    
    def shortest_path(self, start, end):
        import heapq
        
        distances = {vertex: float('infinity') for vertex in self.adjacency_list}
        distances[start] = 0
        priority_queue = [(0, start)]
        previous_vertices = {}
        
        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)
            
            if current_distance > distances[current_vertex]:
                continue
            
            for neighbor, weight in self.adjacency_list[current_vertex]:
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_vertices[neighbor] = current_vertex
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current_vertex = end
        
        while current_vertex != start:
            path.insert(0, current_vertex)
            current_vertex = previous_vertices.get(current_vertex)
            if current_vertex is None:
                return []  # No path exists
        
        path.insert(0, start)
        return path
    
    def find_bottlenecks(self):
        vertex_degrees = []
        
        for vertex, neighbors in self.adjacency_list.items():
            degree = len(neighbors)
            vertex_degrees.append((vertex, degree))
        
        # Sort by degree in descending order
        vertex_degrees.sort(key=lambda x: x[1], reverse=True)
        
        return vertex_degrees
    
    def get_node_connections(self, vertex):
        if vertex not in self.adjacency_list:
            return 0
        return len(self.adjacency_list[vertex])
    