'use client'

import { useEffect, useState } from 'react'
import TriageCard from '@/components/patients/triage-card'
import { patientAPI } from '@/lib/api'
import { Patient } from '@/types/api'

export default function Triage() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPatients = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await patientAPI.getPatients('waiting')
      setPatients(response.data.patients)
    } catch (err) {
      console.error('Error fetching patients:', err)
      setError('Failed to load patients')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPatients()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchPatients, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Patient Triage</h1>
          <p className="text-gray-600 mt-2">Priority-based patient queue management</p>
        </div>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-4 text-gray-600">Loading patients...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!loading && !error && patients.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500 text-lg">No patients waiting for triage</p>
          </div>
        )}

        {!loading && !error && patients.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {patients.map((patient) => (
              <TriageCard 
                key={patient.id} 
                patient={patient}
                onUpdate={fetchPatients}
              />
            ))}
          </div>
        )}

        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Triage Guidelines</h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-sm">
            <div className="bg-red-100 p-3 rounded">
              <div className="font-semibold text-red-800">ESI 1</div>
              <div className="text-red-600">Resuscitation</div>
            </div>
            <div className="bg-orange-100 p-3 rounded">
              <div className="font-semibold text-orange-800">ESI 2</div>
              <div className="text-orange-600">Emergency</div>
            </div>
            <div className="bg-yellow-100 p-3 rounded">
              <div className="font-semibold text-yellow-800">ESI 3</div>
              <div className="text-yellow-600">Urgent</div>
            </div>
            <div className="bg-green-100 p-3 rounded">
              <div className="font-semibold text-green-800">ESI 4</div>
              <div className="text-green-600">Less Urgent</div>
            </div>
            <div className="bg-blue-100 p-3 rounded">
              <div className="font-semibold text-blue-800">ESI 5</div>
              <div className="text-blue-600">Non-Urgent</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}