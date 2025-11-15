'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { resourceAPI } from '@/lib/api'

interface ResourceData {
  name: string
  available: number
  total: number
  color: string
}

export default function ResourceStatus() {
  const [resources, setResources] = useState<ResourceData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchResources = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch rooms
      const roomsResponse = await resourceAPI.getRooms()
      const rooms = roomsResponse.data.rooms
      const availableRooms = rooms.filter((r: any) => r.status === 'available').length

      // Fetch providers
      const providersResponse = await resourceAPI.getProviders()
      const providers = providersResponse.data.providers
      const availableProviders = providers.filter((p: any) => p.is_available).length

      setResources([
        { 
          name: 'Treatment Rooms', 
          available: availableRooms, 
          total: rooms.length, 
          color: 'bg-blue-500' 
        },
        { 
          name: 'Healthcare Providers', 
          available: availableProviders, 
          total: providers.length, 
          color: 'bg-green-500' 
        },
      ])
    } catch (err) {
      console.error('Error fetching resources:', err)
      setError('Failed to load resources')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResources()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchResources, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Resource Status</h3>
          <p className="text-sm text-gray-600">Current availability and utilization</p>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-gray-500">Loading resources...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Resource Status</h3>
          <p className="text-sm text-gray-600">Current availability and utilization</p>
        </CardHeader>
        <CardContent>
          <div className="bg-red-50 border border-red-200 rounded p-3 text-red-600 text-sm">
            {error}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-gray-900">Resource Status</h3>
        <p className="text-sm text-gray-600">Current availability and utilization</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {resources.map((resource, index) => {
            const utilization = resource.total > 0 
              ? Math.round((resource.available / resource.total) * 100)
              : 0
            
            return (
              <div key={index} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium text-gray-700">{resource.name}</span>
                  <span className="text-gray-600">
                    {resource.available}/{resource.total} ({utilization}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${resource.color} transition-all duration-300`}
                    style={{ width: `${utilization}%` }}
                  ></div>
                </div>
              </div>
            )
          })}
        </div>
        
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <span className="font-medium">Optimal resource allocation</span> using graph-based algorithms
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}