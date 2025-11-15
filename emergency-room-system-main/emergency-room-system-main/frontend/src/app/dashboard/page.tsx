'use client'

import { useState, useEffect } from 'react'
import PatientQueue from '@/components/dashboard/patient-queue'
import ResourceStatus from '@/components/dashboard/resource-status'
import RealTimeMetrics from '@/components/dashboard/real-time-metrics'
import { SimpleMetrics } from '@/components/dashboard/simple-metrics'
import { patientAPI } from '@/lib/api'

export default function Dashboard() {
  const [stats, setStats] = useState({ totalPatients: 0, waitingPatients: 0, avgWaitTime: '0 min' })

  const fetchStats = async () => {
    try {
      const response = await patientAPI.getPatients()
      const patients = response.data.patients || []
      
      const totalPatients = patients.length
      const waitingPatients = patients.filter((p: { status: string }) => p.status === 'waiting').length
      
      const waitingTimes = patients
        .filter((p: { status: string; arrival_time?: string }) => p.status === 'waiting')
        .map((p: { status: string; arrival_time?: string }) => {
          if (!p.arrival_time) return 0
          const arrival = new Date(p.arrival_time)
          const now = new Date()
          return (now.getTime() - arrival.getTime()) / 60000
        })
      
      const avgMinutes = waitingTimes.length > 0 
        ? Math.round(waitingTimes.reduce((a: number, b: number) => a + b, 0) / waitingTimes.length)
        : 0
      
      const avgWaitTime = avgMinutes < 60 
        ? `${avgMinutes} min` 
        : `${Math.floor(avgMinutes / 60)}h ${avgMinutes % 60}m`
      
      setStats({ totalPatients, waitingPatients, avgWaitTime })
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
    }
  }

  useEffect(() => {
    fetchStats()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Emergency Room Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time monitoring and management</p>
        </div>

        <RealTimeMetrics stats={stats} />
        
        {/* Performance Metrics Section */}
        <div className="mt-8">
          <SimpleMetrics />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          <PatientQueue />
          <ResourceStatus />
        </div>
      </div>
    </div>
  )
}