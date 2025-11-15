'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { patientAPI } from '@/lib/api'
import { Patient } from '@/types/api'
import ResourceAllocationModal from './resource-allocation-modal'

interface TriageCardProps {
  patient: Patient
  onUpdate?: () => void
}

export default function TriageCard({ patient, onUpdate }: TriageCardProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showAllocationModal, setShowAllocationModal] = useState(false)

  const getESIColor = (esi: number) => {
    switch (esi) {
      case 1: return 'bg-red-100 border-red-300 text-red-800'
      case 2: return 'bg-orange-100 border-orange-300 text-orange-800'
      case 3: return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      case 4: return 'bg-green-100 border-green-300 text-green-800'
      case 5: return 'bg-blue-100 border-blue-300 text-blue-800'
      default: return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  const getESIText = (esi: number) => {
    switch (esi) {
      case 1: return 'Resuscitation'
      case 2: return 'Emergency'
      case 3: return 'Urgent'
      case 4: return 'Less Urgent'
      case 5: return 'Non-Urgent'
      default: return 'Unknown'
    }
  }

  const getPriorityColor = (score: number) => {
    if (score >= 90) return 'bg-red-500'
    if (score >= 70) return 'bg-orange-500'
    if (score >= 50) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const handleStartTreatment = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await patientAPI.startTreatment(patient.id)
      
      // Show success message with resource details if available
      if (response.data.summary) {
        console.log('Treatment started:', response.data.summary)
      }
      
      // Call the onUpdate callback to refresh the list
      if (onUpdate) {
        onUpdate()
      }
      
      // Optionally navigate to the patient details page
      router.push(`/patients/${patient.id}`)
    } catch (err: any) {
      console.error('Error starting treatment:', err)
      const errorMessage = err.response?.data?.detail || 'Failed to start treatment'
      setError(errorMessage)
      setLoading(false)
      
      // Don't reset loading if error - let user see the message
      setTimeout(() => {
        setLoading(false)
      }, 100)
    }
  }

  const handleViewDetails = () => {
    router.push(`/patients/${patient.id}`)
  }

  return (
    <Card className="hover:shadow-lg transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{patient.name}</h3>
            <p className="text-sm text-gray-500">Age: {patient.age} • ID: {patient.id}</p>
          </div>
          <div className={getESIColor(patient.esi_level)}>
            <Badge variant="default">
              ESI {patient.esi_level}
            </Badge>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Chief Complaint:</p>
          <p className="text-gray-900 font-medium">{patient.chief_complaint}</p>
        </div>

        <div className="space-y-3 mb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Priority Score:</span>
            <span className="text-sm font-semibold">{patient.priority_score}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${getPriorityColor(patient.priority_score)} transition-all duration-300`}
              style={{ width: `${Math.min(patient.priority_score, 100)}%` }}
            ></div>
          </div>
        </div>

        <div className="flex justify-between items-center mb-4">
          <div>
            <span className="text-sm text-gray-600">Waiting Time:</span>
            <span className="text-sm font-semibold ml-2">{patient.waiting_time} min</span>
          </div>
          <div className="text-xs text-gray-500">
            {getESIText(patient.esi_level)}
          </div>
        </div>

        {error && (
          <div className="mb-4 text-xs text-red-600 bg-red-50 p-3 rounded border border-red-200">
            <p className="font-medium mb-1">⚠️ Cannot Start Treatment</p>
            <p>{error}</p>
            {error.includes('Allocate Resources') && (
              <a 
                href="/resources" 
                className="text-blue-600 hover:text-blue-800 underline mt-2 inline-block"
              >
                → Go to Resources Page
              </a>
            )}
          </div>
        )}

        <div className="flex space-x-2">
          <Button 
            variant="secondary"
            size="sm" 
            className="flex-1 bg-green-600 hover:bg-green-700 text-white"
            onClick={() => setShowAllocationModal(true)}
            disabled={loading}
          >
            Allocate
          </Button>
          <Button 
            variant="primary" 
            size="sm" 
            className="flex-1"
            onClick={handleStartTreatment}
            disabled={loading}
          >
            {loading ? 'Starting...' : 'Start Treatment'}
          </Button>
          <Button 
            variant="secondary" 
            size="sm"
            onClick={handleViewDetails}
            disabled={loading}
          >
            Details
          </Button>
        </div>
      </CardContent>

      <ResourceAllocationModal
        patient={patient}
        isOpen={showAllocationModal}
        onClose={() => setShowAllocationModal(false)}
        onSuccess={() => {
          if (onUpdate) onUpdate()
        }}
      />
    </Card>
  )
}