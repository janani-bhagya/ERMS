'use client'

import { useRouter } from 'next/navigation'
import { usePatients } from '@/hooks/use-patients'
import { Card, CardHeader, CardContent } from '@/components/ui/card'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const getStatusVariant = (status: string): 'default' | 'success' | 'warning' | 'error' | 'info' => {
  switch (status) {
    case 'in_treatment': return 'info'
    case 'waiting': return 'warning'
    case 'discharged': return 'success'
    case 'admitted': return 'default'
    default: return 'default'
  }
}

const getStatusText = (status: string) => {
  return status.replace('_', ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

const getESIVariant = (level: number): 'default' | 'success' | 'warning' | 'error' | 'info' => {
  if (level === 1) return 'error'
  if (level === 2) return 'warning'
  if (level === 3) return 'info'
  return 'default'
}

export default function PatientList() {
  const router = useRouter()
  const { patients, isLoading, error, dischargePatient } = usePatients()

  const handleRowClick = (patientId: string) => {
    router.push(`/patients/${patientId}`)
  }

  const handleDischarge = (e: React.MouseEvent, patientId: string) => {
    e.stopPropagation() // Prevent row click
    dischargePatient(patientId)
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-4 text-gray-600">Loading patients...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">Error loading patients. Please try again.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!patients || patients.length === 0) {
    return (
      <Card>
        <CardContent>
          <div className="text-center py-12">
            <p className="text-gray-500">No patients found. Add a new patient to get started.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <h2 className="text-xl font-semibold text-gray-900">Patient Queue</h2>
        <p className="text-sm text-gray-500 mt-1">{patients.length} patient{patients.length !== 1 ? 's' : ''} in the system</p>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Patient ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Age</TableHead>
              <TableHead>ESI Level</TableHead>
              <TableHead>Chief Complaint</TableHead>
              <TableHead>Priority Score</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {patients.map((patient) => (
              <TableRow 
                key={patient.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => handleRowClick(patient.id)}
              >
                <TableCell className="font-mono text-xs">{patient.id}</TableCell>
                <TableCell className="font-medium">{patient.name}</TableCell>
                <TableCell>{patient.age}</TableCell>
                <TableCell>
                  <Badge variant={getESIVariant(patient.esi_level)}>
                    Level {patient.esi_level}
                  </Badge>
                </TableCell>
                <TableCell className="max-w-xs truncate">{patient.chief_complaint}</TableCell>
                <TableCell>
                  <span className="font-semibold text-blue-600">
                    {patient.priority_score?.toFixed(1) || 'N/A'}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge variant={getStatusVariant(patient.status)}>
                    {getStatusText(patient.status)}
                  </Badge>
                </TableCell>
                <TableCell>
                  {patient.status !== 'discharged' && (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={(e) => handleDischarge(e, patient.id)}
                    >
                      Discharge
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
