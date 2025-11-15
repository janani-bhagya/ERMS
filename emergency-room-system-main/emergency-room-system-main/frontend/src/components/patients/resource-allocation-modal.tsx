'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { resourceAPI, patientAPI } from '@/lib/api'
import { Patient } from '@/types/api'

interface ResourceAllocationModalProps {
  patient: Patient
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

interface Room {
  id: string
  room_number: string
  room_type: string
  status: string
  current_patient_id: string | null
}

interface Provider {
  id: string
  name: string
  role: string
  specialization: string | null
  is_available: boolean
  current_patient_ids: string[]
}

export default function ResourceAllocationModal({
  patient,
  isOpen,
  onClose,
  onSuccess
}: ResourceAllocationModalProps) {
  const [rooms, setRooms] = useState<Room[]>([])
  const [providers, setProviders] = useState<Provider[]>([])
  const [selectedRoom, setSelectedRoom] = useState<string>('')
  const [selectedProviders, setSelectedProviders] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchResources()
    }
  }, [isOpen])

  const fetchResources = async () => {
    try {
      const [roomsResponse, providersResponse] = await Promise.all([
        resourceAPI.getRooms(),
        resourceAPI.getProviders()
      ])
      setRooms(roomsResponse.data.rooms)
      setProviders(providersResponse.data.providers)
    } catch (err) {
      console.error('Error fetching resources:', err)
      setError('Failed to load resources')
    }
  }

  const handleAllocate = async () => {
    if (!selectedRoom || selectedProviders.length === 0) {
      setError('Please select a room and at least one provider')
      return
    }

    try {
      setLoading(true)
      setError(null)

      await resourceAPI.allocateResources(
        patient.id,
        selectedRoom,
        selectedProviders
      )

      // Success - close modal and refresh
      onSuccess()
      handleClose()
    } catch (err: any) {
      console.error('Error allocating resources:', err)
      setError(err.response?.data?.detail || 'Failed to allocate resources')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setSelectedRoom('')
    setSelectedProviders([])
    setError(null)
    onClose()
  }

  const toggleProvider = (providerId: string) => {
    setSelectedProviders(prev =>
      prev.includes(providerId)
        ? prev.filter(id => id !== providerId)
        : [...prev, providerId]
    )
  }

  const availableRooms = rooms.filter(
    r => !r.current_patient_id && r.status === 'available'
  )
  const availableProviders = providers.filter(p => p.is_available)

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white px-6 py-4">
          <h2 className="text-2xl font-bold">Allocate Resources</h2>
          <p className="text-blue-100 text-sm mt-1">
            Assign room and providers to {patient.name}
          </p>
        </div>

        {/* Patient Info */}
        <div className="px-6 py-4 bg-gray-50 border-b">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Patient:</span>
              <span className="ml-2 font-semibold">{patient.name}</span>
            </div>
            <div>
              <span className="text-gray-600">Age:</span>
              <span className="ml-2 font-semibold">{patient.age}</span>
            </div>
            <div>
              <span className="text-gray-600">ESI Level:</span>
              <span className="ml-2 font-semibold">ESI {patient.esi_level}</span>
            </div>
            <div>
              <span className="text-gray-600">Complaint:</span>
              <span className="ml-2 font-semibold text-xs">{patient.chief_complaint}</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-6 overflow-y-auto max-h-[calc(90vh-280px)]">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Room Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Select Room ({availableRooms.length} available)
              </label>
              <div className="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-3">
                {availableRooms.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No rooms available
                  </p>
                ) : (
                  availableRooms.map((room) => (
                    <div
                      key={room.id}
                      className={`flex items-center gap-3 p-3 rounded cursor-pointer border-2 transition-all ${
                        selectedRoom === room.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                      onClick={() => setSelectedRoom(room.id)}
                    >
                      <input
                        type="radio"
                        checked={selectedRoom === room.id}
                        onChange={() => setSelectedRoom(room.id)}
                        className="cursor-pointer"
                      />
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">
                          {room.room_number}
                        </div>
                        <div className="text-xs text-gray-600 capitalize">
                          {room.room_type}
                        </div>
                      </div>
                      <div className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                        Available
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Provider Selection */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Select Providers ({selectedProviders.length} selected)
              </label>
              <div className="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-3">
                {availableProviders.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No providers available
                  </p>
                ) : (
                  availableProviders.map((provider) => (
                    <div
                      key={provider.id}
                      className={`flex items-center gap-3 p-3 rounded cursor-pointer border-2 transition-all ${
                        selectedProviders.includes(provider.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                      }`}
                      onClick={() => toggleProvider(provider.id)}
                    >
                      <input
                        type="checkbox"
                        checked={selectedProviders.includes(provider.id)}
                        onChange={() => toggleProvider(provider.id)}
                        className="cursor-pointer"
                      />
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900 text-sm">
                          {provider.name}
                        </div>
                        <div className="text-xs text-gray-600">
                          {provider.role}
                          {provider.specialization && ` • ${provider.specialization}`}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Summary */}
          {(selectedRoom || selectedProviders.length > 0) && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded">
              <h3 className="font-semibold text-gray-900 mb-2">Allocation Summary:</h3>
              <div className="text-sm space-y-1">
                {selectedRoom && (
                  <div>
                    <span className="text-gray-600">Room:</span>
                    <span className="ml-2 font-medium">
                      {rooms.find(r => r.id === selectedRoom)?.room_number}
                    </span>
                  </div>
                )}
                {selectedProviders.length > 0 && (
                  <div>
                    <span className="text-gray-600">Providers:</span>
                    <span className="ml-2 font-medium">
                      {selectedProviders.map(id => 
                        providers.find(p => p.id === id)?.name
                      ).join(', ')}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAllocate}
            disabled={!selectedRoom || selectedProviders.length === 0 || loading}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {loading ? 'Allocating...' : 'Allocate Resources'}
          </Button>
        </div>
      </div>
    </div>
  )
}
