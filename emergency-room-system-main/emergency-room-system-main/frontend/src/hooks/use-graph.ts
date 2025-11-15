/**
 * Custom hook for managing graph operations
 * Provides easy access to graph algorithms and resource pathfinding
 */

import { useState, useCallback } from 'react'
import { graphAPI } from '@/lib/api'
import {
  GraphEdge,
  GraphPath,
  BFSResult,
  DFSResult,
  BottlenecksResult,
  ResourceConnections,
} from '@/types/api'

export function useGraph() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const initializeGraph = useCallback(async (edges: GraphEdge[]) => {
    try {
      setLoading(true)
      setError(null)
      const response = await graphAPI.initGraph(edges)
      setLoading(false)
      return response.data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to initialize graph'
      setError(errorMsg)
      setLoading(false)
      throw new Error(errorMsg)
    }
  }, [])

  const findShortestPath = useCallback(async (from: string, to: string): Promise<GraphPath> => {
    try {
      setLoading(true)
      setError(null)
      const response = await graphAPI.getShortestPath(from, to)
      setLoading(false)
      return response.data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to find shortest path'
      setError(errorMsg)
      setLoading(false)
      throw new Error(errorMsg)
    }
  }, [])

  const performBFS = useCallback(
    async (startVertex: string, maxDepth?: number): Promise<BFSResult> => {
      try {
        setLoading(true)
        setError(null)
        const response = await graphAPI.bfs(startVertex, maxDepth)
        setLoading(false)
        return response.data
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to perform BFS'
        setError(errorMsg)
        setLoading(false)
        throw new Error(errorMsg)
      }
    },
    []
  )

  const performDFS = useCallback(
    async (startVertex: string, endVertex?: string): Promise<DFSResult> => {
      try {
        setLoading(true)
        setError(null)
        const response = await graphAPI.dfs(startVertex, endVertex)
        setLoading(false)
        return response.data
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to perform DFS'
        setError(errorMsg)
        setLoading(false)
        throw new Error(errorMsg)
      }
    },
    []
  )

  const getBottlenecks = useCallback(async (): Promise<BottlenecksResult> => {
    try {
      setLoading(true)
      setError(null)
      const response = await graphAPI.getBottlenecks()
      setLoading(false)
      return response.data
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to get bottlenecks'
      setError(errorMsg)
      setLoading(false)
      throw new Error(errorMsg)
    }
  }, [])

  const getResourceConnections = useCallback(
    async (vertex: string): Promise<ResourceConnections> => {
      try {
        setLoading(true)
        setError(null)
        const response = await graphAPI.getResourceConnections(vertex)
        setLoading(false)
        return response.data
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to get resource connections'
        setError(errorMsg)
        setLoading(false)
        throw new Error(errorMsg)
      }
    },
    []
  )

  return {
    loading,
    error,
    initializeGraph,
    findShortestPath,
    performBFS,
    performDFS,
    getBottlenecks,
    getResourceConnections,
  }
}
