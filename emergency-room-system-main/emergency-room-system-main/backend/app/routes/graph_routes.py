"""
Graph Routes for resource optimization and pathfinding.
Demonstrates graph data structure usage with BFS, DFS, and Dijkstra's algorithm.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any

from app.core.graph import Graph

router = APIRouter(prefix="/api/graph", tags=["graph"])

# Global graph instance for ER resources
# In a production system, this would be loaded from database
er_resource_graph = Graph()


class GraphEdgeRequest(BaseModel):
    """Request model for adding edges to the graph"""
    from_vertex: str
    to_vertex: str
    weight: int = 1


class GraphInitRequest(BaseModel):
    """Request model for initializing the graph with multiple edges"""
    edges: List[GraphEdgeRequest]


@router.post("/init")
async def initialize_graph(request: GraphInitRequest):
    """
    Initialize the ER resource graph with edges.
    This sets up the connections between different ER resources.
    """
    try:
        global er_resource_graph
        er_resource_graph = Graph()
        
        for edge in request.edges:
            er_resource_graph.add_edge(
                edge.from_vertex, 
                edge.to_vertex, 
                edge.weight
            )
        
        return {
            "message": "Graph initialized successfully",
            "vertices_count": len(er_resource_graph.get_vertices()),
            "vertices": er_resource_graph.get_vertices()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing graph: {str(e)}")


@router.get("/shortest-path")
async def get_shortest_path(from_vertex: str, to_vertex: str):
    """
    Find shortest path between two resources using Dijkstra's algorithm.
    
    Args:
        from_vertex: Starting resource (e.g., "Triage")
        to_vertex: Destination resource (e.g., "TreatmentRoom")
    
    Returns:
        Shortest path as a list of vertices
    """
    try:
        if from_vertex not in er_resource_graph.adjacency_list:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource '{from_vertex}' not found in graph"
            )
        
        if to_vertex not in er_resource_graph.adjacency_list:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource '{to_vertex}' not found in graph"
            )
        
        path = er_resource_graph.shortest_path(from_vertex, to_vertex)
        
        if not path:
            return {
                "message": f"No path found from {from_vertex} to {to_vertex}",
                "path": []
            }
        
        return {
            "from": from_vertex,
            "to": to_vertex,
            "path": path,
            "steps": len(path) - 1
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding path: {str(e)}")


@router.get("/bfs")
async def breadth_first_search(start_vertex: str, max_depth: Optional[int] = None):
    """
    Perform Breadth-First Search to find all resources within N steps.
    
    Args:
        start_vertex: Starting resource
        max_depth: Maximum depth to traverse (optional)
    
    Returns:
        List of (vertex, depth) tuples
    """
    try:
        if start_vertex not in er_resource_graph.adjacency_list:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource '{start_vertex}' not found in graph"
            )
        
        result = er_resource_graph.bfs(start_vertex, max_depth)
        
        # Convert to more readable format
        resources_by_depth = {}
        for vertex, depth in result:
            if depth not in resources_by_depth:
                resources_by_depth[depth] = []
            resources_by_depth[depth].append(vertex)
        
        return {
            "start": start_vertex,
            "max_depth": max_depth,
            "resources_found": len(result),
            "resources_by_depth": resources_by_depth,
            "all_results": [{"resource": v, "depth": d} for v, d in result]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing BFS: {str(e)}")


@router.get("/dfs")
async def depth_first_search(start_vertex: str, end_vertex: Optional[str] = None):
    """
    Perform Depth-First Search to trace workflow path.
    
    Args:
        start_vertex: Starting resource
        end_vertex: Target resource (optional)
    
    Returns:
        List of vertices in DFS traversal order
    """
    try:
        if start_vertex not in er_resource_graph.adjacency_list:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource '{start_vertex}' not found in graph"
            )
        
        if end_vertex and end_vertex not in er_resource_graph.adjacency_list:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource '{end_vertex}' not found in graph"
            )
        
        path = er_resource_graph.dfs(start_vertex, end_vertex)
        
        return {
            "start": start_vertex,
            "end": end_vertex,
            "path": path,
            "steps": len(path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing DFS: {str(e)}")


@router.get("/bottlenecks")
async def find_bottlenecks():
    """
    Find potential bottleneck resources (nodes with most connections).
    Resources with high connectivity are potential bottlenecks in patient flow.
    
    Returns:
        List of (vertex, connection_count) sorted by connectivity
    """
    try:
        bottlenecks = er_resource_graph.find_bottlenecks()
        
        return {
            "message": "Resources sorted by connectivity (potential bottlenecks)",
            "total_resources": len(bottlenecks),
            "bottlenecks": [
                {"resource": vertex, "connections": count} 
                for vertex, count in bottlenecks
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding bottlenecks: {str(e)}")


@router.get("/vertices")
async def list_vertices():
    """
    List all vertices (resources) in the graph.
    """
    try:
        vertices = er_resource_graph.get_vertices()
        
        return {
            "vertices": vertices,
            "count": len(vertices)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing vertices: {str(e)}")


@router.get("/resource/{vertex}/connections")
async def get_resource_connections(vertex: str):
    """
    Get the number of connections for a specific resource.
    
    Args:
        vertex: Resource name
    
    Returns:
        Number of connections and list of neighbors
    """
    try:
        if vertex not in er_resource_graph.adjacency_list:
            raise HTTPException(
                status_code=404, 
                detail=f"Resource '{vertex}' not found in graph"
            )
        
        connections = er_resource_graph.get_node_connections(vertex)
        neighbors = er_resource_graph.get_neighbors(vertex)
        
        return {
            "resource": vertex,
            "connection_count": connections,
            "neighbors": [
                {"resource": neighbor, "weight": weight} 
                for neighbor, weight in neighbors
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting connections: {str(e)}")
