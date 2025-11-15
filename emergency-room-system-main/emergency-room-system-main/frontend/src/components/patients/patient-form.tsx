'use client'

import { useState } from 'react'
import { usePatients } from '@/hooks/use-patients'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { PatientCreate } from '@/types/api'

interface PatientFormProps {
  onClose: () => void
}

export default function PatientForm({ onClose }: PatientFormProps) {
  const { addPatient, isAdding } = usePatients()
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    esi_level: '3',
    chief_complaint: '',
    heart_rate: '',
    blood_pressure: '',
    temperature: '',
    respiratory_rate: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    const patientData: PatientCreate = {
      name: formData.name,
      age: parseInt(formData.age),
      esi_level: parseInt(formData.esi_level) as 1 | 2 | 3 | 4 | 5,
      chief_complaint: formData.chief_complaint,
      vital_signs: {
        heart_rate: formData.heart_rate ? parseInt(formData.heart_rate) : undefined,
        blood_pressure: formData.blood_pressure || undefined,
        temperature: formData.temperature ? parseFloat(formData.temperature) : undefined,
        respiratory_rate: formData.respiratory_rate ? parseInt(formData.respiratory_rate) : undefined,
      }
    }

    addPatient(patientData, {
      onSuccess: () => {
        onClose()
      }
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="max-w-2xl w-full mx-4">
        <CardHeader>
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Add New Patient</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-1">
                  Age *
                </label>
                <input
                  type="number"
                  id="age"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  min="0"
                />
              </div>
            </div>

            <div>
              <label htmlFor="esi_level" className="block text-sm font-medium text-gray-700 mb-1">
                ESI Level *
              </label>
              <select
                id="esi_level"
                value={formData.esi_level}
                onChange={(e) => setFormData({ ...formData, esi_level: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="1">Level 1 - Resuscitation (Immediate)</option>
                <option value="2">Level 2 - Emergency (10-15 min)</option>
                <option value="3">Level 3 - Urgent (30-60 min)</option>
                <option value="4">Level 4 - Less Urgent (1-2 hours)</option>
                <option value="5">Level 5 - Non-Urgent (2-24 hours)</option>
              </select>
            </div>

            <div>
              <label htmlFor="chief_complaint" className="block text-sm font-medium text-gray-700 mb-1">
                Chief Complaint *
              </label>
              <textarea
                id="chief_complaint"
                value={formData.chief_complaint}
                onChange={(e) => setFormData({ ...formData, chief_complaint: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                required
              />
            </div>

            <div className="border-t pt-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Vital Signs</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="heart_rate" className="block text-sm font-medium text-gray-700 mb-1">
                    Heart Rate (bpm)
                  </label>
                  <input
                    type="number"
                    id="heart_rate"
                    value={formData.heart_rate}
                    onChange={(e) => setFormData({ ...formData, heart_rate: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="blood_pressure" className="block text-sm font-medium text-gray-700 mb-1">
                    Blood Pressure (e.g., 120/80)
                  </label>
                  <input
                    type="text"
                    id="blood_pressure"
                    value={formData.blood_pressure}
                    onChange={(e) => setFormData({ ...formData, blood_pressure: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 mb-1">
                    Temperature (°F)
                  </label>
                  <input
                    type="number"
                    id="temperature"
                    step="0.1"
                    value={formData.temperature}
                    onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="respiratory_rate" className="block text-sm font-medium text-gray-700 mb-1">
                    Respiratory Rate
                  </label>
                  <input
                    type="number"
                    id="respiratory_rate"
                    value={formData.respiratory_rate}
                    onChange={(e) => setFormData({ ...formData, respiratory_rate: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6 pt-4 border-t">
              <Button
                type="button"
                onClick={onClose}
                variant="secondary"
                disabled={isAdding}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isAdding}
              >
                {isAdding ? 'Creating...' : 'Create Patient'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
