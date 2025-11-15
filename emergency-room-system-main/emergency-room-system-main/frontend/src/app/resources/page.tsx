'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { resourceAPI, patientAPI } from '@/lib/api'
import { useGraph } from '@/hooks/use-graph'

interface Room {
  id: string
  room_number: string
  room_type: string
  status: string
  current_patient_id: string | null
  equipment_ids: string[]
}

interface Provider {
  id: string
  name: string
  role: string
  specialization: string | null
  is_available: boolean
  current_patient_ids: string[]
}

interface Patient {
  id: string
  name: string
  age: number
  esi_level: number
  chief_complaint: string
  status: string
  priority_score: number
}

export default function Resources() {
  const [rooms, setRooms] = useState<Room[]>([])
  const [providers, setProviders] = useState<Provider[]>([])
  const [waitingPatients, setWaitingPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Allocation state
  const [showAllocationDialog, setShowAllocationDialog] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const [selectedRoomForAllocation, setSelectedRoomForAllocation] = useState<string>('')
  const [selectedProvidersForAllocation, setSelectedProvidersForAllocation] = useState<string[]>([])
  const [allocating, setAllocating] = useState(false)
  
  // Graph analysis
  const { initializeGraph, findShortestPath, getBottlenecks } = useGraph()
  const [graphInitialized, setGraphInitialized] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [bottlenecks, setBottlenecks] = useState<any>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [shortestPath, setShortestPath] = useState<any>(null)
  const [selectedFrom, setSelectedFrom] = useState<string>('')
  const [selectedTo, setSelectedTo] = useState<string>('')
  
  // Resource management
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null)
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null)

  useEffect(() => {
    fetchResources()
    fetchWaitingPatients()
  }, [])

  const fetchResources = async () => {
    try {
      setLoading(true)
      setError(null)

      const [roomsResponse, providersResponse] = await Promise.all([
        resourceAPI.getRooms(),
        resourceAPI.getProviders()
      ])

      setRooms(roomsResponse.data.rooms)
      setProviders(providersResponse.data.providers)
    } catch (err) {
      console.error('Error fetching resources:', err)
      setError('Failed to load resources')
    } finally {
      setLoading(false)
    }
  }

  const fetchWaitingPatients = async () => {
    try {
      const response = await patientAPI.getPatients('waiting')
      setWaitingPatients(response.data.patients)
    } catch (err) {
      console.error('Error fetching waiting patients:', err)
    }
  }

  const handleAllocateResources = async () => {
    if (!selectedPatient || !selectedRoomForAllocation || selectedProvidersForAllocation.length === 0) {
      alert('Please select a patient, room, and at least one provider')
      return
    }

    try {
      setAllocating(true)
      await resourceAPI.allocateResources(
        selectedPatient.id,
        selectedRoomForAllocation,
        selectedProvidersForAllocation
      )
      
      // Refresh data
      await fetchResources()
      await fetchWaitingPatients()
      
      // Reset form
      setShowAllocationDialog(false)
      setSelectedPatient(null)
      setSelectedRoomForAllocation('')
      setSelectedProvidersForAllocation([])
      
      alert(`Successfully allocated resources to ${selectedPatient.name}`)
    } catch (err) {
      console.error('Error allocating resources:', err)
      alert('Failed to allocate resources. Please try again.')
    } finally {
      setAllocating(false)
    }
  }

  const toggleProviderSelection = (providerId: string) => {
    setSelectedProvidersForAllocation(prev => 
      prev.includes(providerId)
        ? prev.filter(id => id !== providerId)
        : [...prev, providerId]
    )
  }

  const handleInitializeGraph = async () => {
    try {
      // Create sample ER resource graph
      const edges = [
        { from_vertex: 'Triage', to_vertex: 'WaitingRoom', weight: 1 },
        { from_vertex: 'WaitingRoom', to_vertex: 'TreatmentRoom1', weight: 2 },
        { from_vertex: 'WaitingRoom', to_vertex: 'TreatmentRoom2', weight: 2 },
        { from_vertex: 'TreatmentRoom1', to_vertex: 'XRay', weight: 3 },
        { from_vertex: 'TreatmentRoom2', to_vertex: 'XRay', weight: 2 },
        { from_vertex: 'TreatmentRoom1', to_vertex: 'Lab', weight: 2 },
        { from_vertex: 'TreatmentRoom2', to_vertex: 'Lab', weight: 3 },
        { from_vertex: 'XRay', to_vertex: 'Discharge', weight: 2 },
        { from_vertex: 'Lab', to_vertex: 'Discharge', weight: 2 },
        { from_vertex: 'Triage', to_vertex: 'EmergencyRoom', weight: 1 },
        { from_vertex: 'EmergencyRoom', to_vertex: 'ICU', weight: 1 },
      ]

      await initializeGraph(edges)
      setGraphInitialized(true)
      
      // Automatically analyze bottlenecks
      await analyzeBottlenecks()
    } catch (err) {
      console.error('Error initializing graph:', err)
    }
  }

  const analyzeBottlenecks = async () => {
    try {
      const result = await getBottlenecks()
      setBottlenecks(result)
    } catch (err) {
      console.error('Error analyzing bottlenecks:', err)
    }
  }

  const handleFindPath = async () => {
    if (!selectedFrom || !selectedTo) return
    
    try {
      const result = await findShortestPath(selectedFrom, selectedTo)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      setShortestPath(result as any)
    } catch (err) {
      console.error('Error finding path:', err)
    }
  }

  const calculateUtilization = (available: number, total: number) => {
    return total > 0 ? Math.round(((total - available) / total) * 100) : 0
  }

  const availableRooms = rooms.filter(r => r.status === 'available' && !r.current_patient_id).length
  const availableProviders = providers.filter(p => p.is_available && (!p.current_patient_ids || p.current_patient_ids.length === 0)).length
  
  const roomUtilization = calculateUtilization(availableRooms, rooms.length)
  const providerUtilization = calculateUtilization(availableProviders, providers.length)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-4 text-gray-600">Loading resources...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Resource Management</h1>
          <p className="text-gray-600 mt-2">Graph-based optimization and bottleneck detection</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Resource Allocation Section */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Resource Allocation</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Assign rooms and providers to waiting patients
                </p>
              </div>
              <Button 
                onClick={() => setShowAllocationDialog(!showAllocationDialog)}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                {showAllocationDialog ? 'Hide' : 'Allocate Resources'}
              </Button>
            </div>
          </CardHeader>
          {showAllocationDialog && (
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Select Patient */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Select Waiting Patient ({waitingPatients.length})
                  </label>
                  <select 
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    value={selectedPatient?.id || ''}
                    onChange={(e) => {
                      const patient = waitingPatients.find(p => p.id === e.target.value)
                      setSelectedPatient(patient || null)
                    }}
                  >
                    <option value="">Choose patient...</option>
                    {waitingPatients.map((patient) => (
                      <option key={patient.id} value={patient.id}>
                        {patient.name} (ESI-{patient.esi_level}, Priority: {patient.priority_score.toFixed(0)})
                      </option>
                    ))}
                  </select>
                  {selectedPatient && (
                    <div className="mt-2 p-3 bg-blue-50 rounded text-xs">
                      <p><strong>Age:</strong> {selectedPatient.age}</p>
                      <p><strong>Complaint:</strong> {selectedPatient.chief_complaint}</p>
                    </div>
                  )}
                </div>

                {/* Select Room */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Select Available Room
                  </label>
                  <select 
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    value={selectedRoomForAllocation}
                    onChange={(e) => setSelectedRoomForAllocation(e.target.value)}
                  >
                    <option value="">Choose room...</option>
                    {rooms.filter(r => !r.current_patient_id && r.status === 'available').map((room) => (
                      <option key={room.id} value={room.id}>
                        {room.room_number} - {room.room_type}
                      </option>
                    ))}
                  </select>
                  {selectedRoomForAllocation && (
                    <div className="mt-2 p-3 bg-green-50 rounded text-xs">
                      {rooms.find(r => r.id === selectedRoomForAllocation)?.room_number} selected
                    </div>
                  )}
                </div>

                {/* Select Providers */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Select Providers (multi-select)
                  </label>
                  <div className="border border-gray-300 rounded-lg max-h-48 overflow-y-auto p-2 space-y-1">
                    {providers.filter(p => p.is_available).map((provider) => (
                      <div 
                        key={provider.id}
                        className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-gray-100 ${
                          selectedProvidersForAllocation.includes(provider.id) ? 'bg-blue-100' : ''
                        }`}
                        onClick={() => toggleProviderSelection(provider.id)}
                      >
                        <input 
                          type="checkbox"
                          checked={selectedProvidersForAllocation.includes(provider.id)}
                          onChange={() => toggleProviderSelection(provider.id)}
                          className="cursor-pointer"
                        />
                        <span className="text-xs">{provider.name} ({provider.role})</span>
                      </div>
                    ))}
                  </div>
                  {selectedProvidersForAllocation.length > 0 && (
                    <div className="mt-2 p-3 bg-green-50 rounded text-xs">
                      {selectedProvidersForAllocation.length} provider(s) selected
                    </div>
                  )}
                </div>
              </div>

              {/* Allocate Button */}
              <div className="mt-6 flex justify-end gap-3">
                <Button 
                  variant="secondary"
                  onClick={() => {
                    setShowAllocationDialog(false)
                    setSelectedPatient(null)
                    setSelectedRoomForAllocation('')
                    setSelectedProvidersForAllocation([])
                  }}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleAllocateResources}
                  disabled={!selectedPatient || !selectedRoomForAllocation || selectedProvidersForAllocation.length === 0 || allocating}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  {allocating ? 'Allocating...' : 'Confirm Allocation'}
                </Button>
              </div>
            </CardContent>
          )}
        </Card>

        {/* Resource Management Table */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Rooms Management */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">Treatment Rooms ({rooms.length})</h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {rooms.map((room) => {
                  const isOccupied = room.current_patient_id !== null
                  return (
                    <div 
                      key={room.id}
                      className={`flex justify-between items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedRoom?.id === room.id ? 'border-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedRoom(room)}
                    >
                      <div>
                        <p className="font-medium text-sm">{room.room_number}</p>
                        <p className="text-xs text-gray-500 capitalize">{room.room_type}</p>
                        {isOccupied && (
                          <p className="text-xs text-blue-600 mt-1">Patient: {room.current_patient_id}</p>
                        )}
                      </div>
                      <Badge variant={isOccupied ? 'default' : 'success'}>
                        {isOccupied ? 'Occupied' : 'Available'}
                      </Badge>
                    </div>
                  )
                })}
              </div>
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  Available: <strong>{availableRooms}</strong> / {rooms.length}
                </p>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${roomUtilization > 80 ? 'bg-red-500' : roomUtilization > 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${roomUtilization}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{roomUtilization}% occupied</p>
              </div>
            </CardContent>
          </Card>

          {/* Providers Management */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">Healthcare Providers ({providers.length})</h3>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {providers.map((provider) => {
                  const isBusy = provider.current_patient_ids && provider.current_patient_ids.length > 0
                  return (
                    <div 
                      key={provider.id}
                      className={`flex justify-between items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                        selectedProvider?.id === provider.id ? 'border-blue-500 bg-blue-50' : 'hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedProvider(provider)}
                    >
                      <div>
                        <p className="font-medium text-sm">{provider.name}</p>
                        <p className="text-xs text-gray-500 capitalize">{provider.role} {provider.specialization && `- ${provider.specialization}`}</p>
                        {isBusy && (
                          <p className="text-xs text-blue-600 mt-1">
                            Patients: {provider.current_patient_ids.length}
                          </p>
                        )}
                      </div>
                      <Badge variant={isBusy ? 'default' : 'success'}>
                        {isBusy ? 'Busy' : 'Available'}
                      </Badge>
                    </div>
                  )
                })}
              </div>
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-600">
                  Available: <strong>{availableProviders}</strong> / {providers.length}
                </p>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${providerUtilization > 80 ? 'bg-red-500' : providerUtilization > 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${providerUtilization}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">{providerUtilization}% busy</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Selected Resource Details */}
        {(selectedRoom || selectedProvider) && (
          <Card className="mb-8">
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">
                Resource Details: {selectedRoom ? selectedRoom.room_number : selectedProvider?.name}
              </h3>
            </CardHeader>
            <CardContent>
              {selectedRoom ? (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Room ID:</span>
                    <span className="font-medium">{selectedRoom.id}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Room Number:</span>
                    <span className="font-medium">{selectedRoom.room_number}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Room Type:</span>
                    <span className="font-medium capitalize">{selectedRoom.room_type}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <Badge variant={selectedRoom.current_patient_id ? 'default' : 'success'}>
                      {selectedRoom.current_patient_id ? 'Occupied' : 'Available'}
                    </Badge>
                  </div>
                  {selectedRoom.current_patient_id && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Current Patient:</span>
                      <span className="font-medium text-blue-600">{selectedRoom.current_patient_id}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Equipment:</span>
                    <span className="font-medium">
                      {selectedRoom.equipment_ids.length > 0 ? selectedRoom.equipment_ids.length : 'None'}
                    </span>
                  </div>
                </div>
              ) : selectedProvider ? (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Provider ID:</span>
                    <span className="font-medium">{selectedProvider.id}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Name:</span>
                    <span className="font-medium">{selectedProvider.name}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Role:</span>
                    <span className="font-medium capitalize">{selectedProvider.role}</span>
                  </div>
                  {selectedProvider.specialization && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Specialization:</span>
                      <span className="font-medium">{selectedProvider.specialization}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <Badge variant={selectedProvider.current_patient_ids.length > 0 ? 'default' : 'success'}>
                      {selectedProvider.current_patient_ids.length > 0 ? 'Busy' : 'Available'}
                    </Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Current Patients:</span>
                    <span className="font-medium">
                      {selectedProvider.current_patient_ids.length > 0 
                        ? selectedProvider.current_patient_ids.length 
                        : 'None'}
                    </span>
                  </div>
                  {selectedProvider.current_patient_ids.length > 0 && (
                    <div className="mt-2 pt-2 border-t">
                      <p className="text-xs text-gray-600 mb-1">Patient IDs:</p>
                      <div className="flex flex-wrap gap-1">
                        {selectedProvider.current_patient_ids.map((pid) => (
                          <Badge key={pid} variant="info">{pid}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : null}
              <p className="text-xs text-gray-500 mt-4 pt-4 border-t">
                Click on a different resource to view its details, or use graph algorithms below for optimization analysis.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Graph-Based Analysis */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Graph-Based Resource Optimization</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Uses Dijkstra&apos;s algorithm for pathfinding and connection analysis for bottleneck detection
                </p>
              </div>
              <Button 
                onClick={handleInitializeGraph}
                disabled={graphInitialized}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {graphInitialized ? '✓ Graph Initialized' : 'Initialize Graph'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {!graphInitialized ? (
              <div className="text-center py-8 text-gray-500">
                Click &quot;Initialize Graph&quot; to start graph-based analysis
              </div>
            ) : (
              <div className="space-y-6">
                {/* Bottleneck Detection */}
                {bottlenecks && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      Bottleneck Detection (Most Connected Resources)
                    </h3>
                    <div className="space-y-2">
                      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                      {bottlenecks.bottlenecks?.slice(0, 3).map((item: any, idx: number) => (
                        <div key={idx} className="flex justify-between items-center">
                          <span className="text-sm font-medium">{item.resource}</span>
                          <Badge variant={item.connections > 2 ? 'error' : 'warning'}>
                            {item.connections} connections
                          </Badge>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-600 mt-3">
                      Resources with more connections are potential bottlenecks in patient flow
                    </p>
                  </div>
                )}

                {/* Shortest Path Finder */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3">
                    Find Shortest Path (Dijkstra's Algorithm)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <select 
                      className="border border-gray-300 rounded px-3 py-2 text-sm"
                      value={selectedFrom}
                      onChange={(e) => setSelectedFrom(e.target.value)}
                    >
                      <option value="">From...</option>
                      <option value="Triage">Triage</option>
                      <option value="WaitingRoom">Waiting Room</option>
                      <option value="TreatmentRoom1">Treatment Room 1</option>
                      <option value="TreatmentRoom2">Treatment Room 2</option>
                      <option value="XRay">X-Ray</option>
                      <option value="Lab">Laboratory</option>
                      <option value="EmergencyRoom">Emergency Room</option>
                      <option value="ICU">ICU</option>
                    </select>
                    <select 
                      className="border border-gray-300 rounded px-3 py-2 text-sm"
                      value={selectedTo}
                      onChange={(e) => setSelectedTo(e.target.value)}
                    >
                      <option value="">To...</option>
                      <option value="Triage">Triage</option>
                      <option value="WaitingRoom">Waiting Room</option>
                      <option value="TreatmentRoom1">Treatment Room 1</option>
                      <option value="TreatmentRoom2">Treatment Room 2</option>
                      <option value="XRay">X-Ray</option>
                      <option value="Lab">Laboratory</option>
                      <option value="Discharge">Discharge</option>
                      <option value="EmergencyRoom">Emergency Room</option>
                      <option value="ICU">ICU</option>
                    </select>
                    <Button 
                      onClick={handleFindPath}
                      disabled={!selectedFrom || !selectedTo}
                      variant="secondary"
                    >
                      Find Path
                    </Button>
                  </div>
                  {shortestPath && shortestPath.path && (
                    <div className="mt-3 p-3 bg-white rounded border border-blue-300">
                      <p className="text-sm font-medium mb-2">
                        Shortest Path (distance: {shortestPath.distance || shortestPath.steps || 'N/A'}):
                      </p>
                      <div className="flex items-center gap-2 flex-wrap">
                        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                        {shortestPath.path.map((vertex: any, idx: number) => (
                          <span key={idx} className="flex items-center">
                            <Badge variant="info">{vertex}</Badge>
                            {idx < shortestPath.path.length - 1 && (
                              <span className="mx-2 text-gray-400">→</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}