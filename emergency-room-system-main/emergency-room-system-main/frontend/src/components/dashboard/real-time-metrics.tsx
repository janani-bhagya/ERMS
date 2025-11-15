'use client'

import { Card, CardContent } from '@/components/ui/card'

interface MetricsProps {
  stats: {
    totalPatients: number
    waitingPatients: number
    avgWaitTime: number
    resourceUtilization: number
  }
}

export default function RealTimeMetrics({ stats }: {
  stats: {
    totalPatients: number
    waitingPatients: number
    avgWaitTime: string
  }
}) {
  const metrics = [
    {
      label: 'Total Patients',
      value: stats.totalPatients,
      change: '+12%',
      trend: 'up',
      color: 'bg-blue-500'
    },
    {
      label: 'Waiting Patients',
      value: stats.waitingPatients,
      change: '-5%',
      trend: 'down',
      color: 'bg-orange-500'
    },
    {
      label: 'Avg Wait Time',
      value: stats.avgWaitTime,
      change: '',
      trend: 'neutral',
      color: 'bg-yellow-500'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metrics.map((metric, index) => (
        <Card key={index} className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className={`w-12 h-12 ${metric.color} rounded-lg flex items-center justify-center`}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{metric.label}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-gray-900">{metric.value}</p>
                  <span className={`ml-2 text-sm font-medium ${
                    metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metric.change}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}