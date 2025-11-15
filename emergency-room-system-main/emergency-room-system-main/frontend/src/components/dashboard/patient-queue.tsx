'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { patientAPI } from '@/lib/api'
import { Patient } from '@/types/api'

const getESIVariant = (esi: number): 'default' | 'success' | 'warning' | 'error' | 'info' => {
  switch (esi) {
    case 1: return 'error'
    case 2: return 'warning'
    case 3: return 'info'
    case 4: return 'success'
    case 5: return 'default'
    default: return 'default'
  }
}



export default function PatientQueue() {
  const router = useRouter()
  const [patients, setPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPatients = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await patientAPI.getPatients('waiting')
      // Sort by priority score (highest first)
      const sortedPatients = response.data.patients.sort((a, b) => 
        (b.priority_score || 0) - (a.priority_score || 0)
      )
      setPatients(sortedPatients.slice(0, 5)) // Show top 5
    } catch (err) {
      console.error('Error fetching patients:', err)
      setError('Failed to load patient queue')
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

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Patient Queue</h3>
          <p className="text-sm text-gray-600">Real-time patient waiting list</p>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-gray-500">Loading queue...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold text-gray-900">Patient Queue</h3>
          <p className="text-sm text-gray-600">Real-time patient waiting list</p>
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
        <h3 className="text-lg font-semibold text-gray-900">Patient Queue</h3>
        <p className="text-sm text-gray-600">Top {patients.length} priority patients waiting</p>
      </CardHeader>
      <CardContent>
        {patients.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No patients waiting
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient</TableHead>
                <TableHead>ESI</TableHead>
                <TableHead>Waiting</TableHead>
                <TableHead>Complaint</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {patients.map((patient) => (
                <TableRow 
                  key={patient.id}
                  className="cursor-pointer hover:bg-gray-50"
                  onClick={() => router.push(`/patients/${patient.id}`)}
                >
                  <TableCell>
                    <div>
                      <div className="font-medium text-gray-900">{patient.name}</div>
                      <div className="text-sm text-gray-500">{patient.id}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getESIVariant(patient.esi_level)}>
                      ESI {patient.esi_level}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-gray-900">{patient.waiting_time} min</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-gray-600 truncate max-w-xs">
                      {patient.chief_complaint}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}