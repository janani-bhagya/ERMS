import { useEffect, useRef, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'
import { useQueryClient } from '@tanstack/react-query'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000'

export const useWebSocket = () => {
  const socketRef = useRef<Socket | null>(null)
  const queryClient = useQueryClient()

  useEffect(() => {
    // Initialize socket connection
    socketRef.current = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })

    const socket = socketRef.current

    // Connection events
    socket.on('connect', () => {
      console.log('WebSocket connected:', socket.id)
    })

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })

    socket.on('connection_status', (data) => {
      console.log('Connection status:', data)
    })

    // Real-time data events
    socket.on('patient_update', (data) => {
      console.log('Patient update received:', data)
      // Invalidate patients query to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['patients'] })
    })

    socket.on('triage_update', (data) => {
      console.log('Triage update received:', data)
      queryClient.invalidateQueries({ queryKey: ['triage'] })
    })

    socket.on('resource_update', (data) => {
      console.log('Resource update received:', data)
      queryClient.invalidateQueries({ queryKey: ['resources'] })
    })

    socket.on('metrics_update', (data) => {
      console.log('Metrics update received:', data)
      queryClient.invalidateQueries({ queryKey: ['metrics'] })
    })

    socket.on('patient_status', (data) => {
      console.log('Patient status change:', data)
      queryClient.invalidateQueries({ queryKey: ['patients'] })
      queryClient.invalidateQueries({ queryKey: ['patient', data.patient_id] })
    })

    // Cleanup on unmount
    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [queryClient])

  const subscribe = useCallback((channel: string) => {
    if (socketRef.current) {
      socketRef.current.emit('subscribe', { channel })
    }
  }, [])

  return {
    socket: socketRef.current,
    subscribe,
    isConnected: socketRef.current?.connected || false,
  }
}