'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { patientAPI, treatmentAPI } from '@/lib/api'
import { Patient } from '@/types/api'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export default function PatientDetail() {
  const params = useParams()
  const router = useRouter()
  const patientId = params.id as string
  
  const [patient, setPatient] = useState<Patient | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [treatmentHistory, setTreatmentHistory] = useState<Array<{
    id: string
    action_type: string
    performed_by: string
    details: Record<string, unknown>
    notes?: string
    timestamp: string
  }>>([])
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const fetchPatient = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await patientAPI.getPatient(patientId)
      setPatient(response.data)
      
      // Try to fetch treatment history
      try {
        const historyResponse = await treatmentAPI.getHistory(patientId)
        setTreatmentHistory(historyResponse.data.history || [])
      } catch {
        // Treatment history might not exist yet
        console.log('No treatment history yet')
      }
    } catch (err: unknown) {
      console.error('Error fetching patient:', err)
      setError((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Failed to load patient details')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (patientId) {
      fetchPatient()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patientId])

  const handleStartTreatment = async () => {
    setActionLoading(true)
    setActionError(null)
    
    try {
      const response = await patientAPI.startTreatment(patientId)
      
      // Show success message with resource details if available
      if (response.data && 'summary' in response.data) {
        console.log('Treatment started:', (response.data as any).summary)
      }
      
      // Refresh patient data
      await fetchPatient()
    } catch (err: unknown) {
      console.error('Error starting treatment:', err)
      const errorDetail = (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Failed to start treatment'
      setActionError(errorDetail)
    } finally {
      setActionLoading(false)
    }
  }

  const handleDischarge = async () => {
    if (!confirm('Are you sure you want to discharge this patient?')) {
      return
    }
    
    setActionLoading(true)
    setActionError(null)
    
    try {
      await patientAPI.dischargePatient(patientId)
      // Refresh patient data
      await fetchPatient()
    } catch (err: unknown) {
      console.error('Error discharging patient:', err)
      setActionError((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Failed to discharge patient')
    } finally {
      setActionLoading(false)
    }
  }

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

  const getStatusBadgeVariant = (status: string): 'default' | 'success' | 'warning' | 'error' | 'info' => {
    switch (status) {
      case 'waiting': return 'warning'
      case 'in_treatment': return 'info'
      case 'discharged': return 'success'
      default: return 'default'
    }
  }

  const formatStatus = (status: string) => {
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-4 text-gray-600">Loading patient details...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !patient) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
            {error || 'Patient not found'}
          </div>
          <Button onClick={() => router.back()}>Go Back</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{patient.name}</h1>
            <p className="text-gray-600 mt-2">Patient ID: {patient.id}</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => router.back()} variant="secondary">
              Back
            </Button>
          </div>
        </div>

        {/* Action Error Alert */}
        {actionError && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            <p className="font-medium mb-1">⚠️ Action Failed</p>
            <p className="text-sm">{actionError}</p>
            {actionError.includes('Allocate Resources') && (
              <a 
                href="/resources" 
                className="text-blue-600 hover:text-blue-800 text-sm underline mt-2 inline-block"
              >
                → Go to Resources Page to Allocate Room & Providers
              </a>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="mb-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Patient Actions</h2>
          <div className="flex gap-3">
            {patient.status === 'waiting' && (
              <Button
                onClick={handleStartTreatment}
                disabled={actionLoading}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                {actionLoading ? 'Starting...' : 'Start Treatment'}
              </Button>
            )}
            {(patient.status === 'waiting' || patient.status === 'in_treatment') && (
              <Button
                onClick={handleDischarge}
                disabled={actionLoading}
                variant="secondary"
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                {actionLoading ? 'Discharging...' : 'Discharge Patient'}
              </Button>
            )}
            {patient.status === 'discharged' && (
              <div className="text-gray-500 italic">
                Patient has been discharged
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Patient Overview Card */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Patient Information</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Age:</span>
                  <span className="font-medium">{patient.age} years</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">ESI Level:</span>
                  <div className={getESIColor(patient.esi_level)}>
                    <Badge variant="default">
                      ESI {patient.esi_level} - {getESIText(patient.esi_level)}
                    </Badge>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <Badge variant={getStatusBadgeVariant(patient.status)}>
                    {formatStatus(patient.status)}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Priority Score:</span>
                  <span className="font-medium">{patient.priority_score}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Waiting Time:</span>
                  <span className="font-medium">{patient.waiting_time} minutes</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Chief Complaint Card */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Chief Complaint</h2>
              <p className="text-gray-700">{patient.chief_complaint}</p>
            </CardContent>
          </Card>
        </div>

        {/* Vital Signs Card */}
        {patient.vital_signs && (
          <Card className="mb-6">
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Vital Signs</h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {patient.vital_signs.bp && (
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-600 mb-1">Blood Pressure</div>
                    <div className="text-lg font-semibold">{patient.vital_signs.bp}</div>
                  </div>
                )}
                {patient.vital_signs.hr && (
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-600 mb-1">Heart Rate</div>
                    <div className="text-lg font-semibold">{patient.vital_signs.hr} bpm</div>
                  </div>
                )}
                {patient.vital_signs.temp && (
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-600 mb-1">Temperature</div>
                    <div className="text-lg font-semibold">{patient.vital_signs.temp}°F</div>
                  </div>
                )}
                {patient.vital_signs.rr && (
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-600 mb-1">Resp. Rate</div>
                    <div className="text-lg font-semibold">{patient.vital_signs.rr}/min</div>
                  </div>
                )}
                {patient.vital_signs.spo2 && (
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-xs text-gray-600 mb-1">SpO2</div>
                    <div className="text-lg font-semibold">{patient.vital_signs.spo2}%</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Treatment History Card */}
        {treatmentHistory.length > 0 && (
          <Card>
            <CardContent className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Treatment History</h2>
              <div className="space-y-3">
                {treatmentHistory.map((item, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="font-medium">{item.action_type}</div>
                    <div className="text-sm text-gray-600">{JSON.stringify(item.details)}</div>
                    <div className="text-xs text-gray-500">{item.timestamp}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}