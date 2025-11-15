'use client'

import { useState } from 'react'
import PatientList from '@/components/patients/patient-list'
import PatientForm from '@/components/patients/patient-form'

export default function Patients() {
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Patient Management</h1>
            <p className="text-gray-600 mt-2">Manage patient records and treatment plans</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add New Patient
          </button>
        </div>

        {showForm && (
          <PatientForm onClose={() => setShowForm(false)} />
        )}

        <PatientList />
      </div>
    </div>
  )
}