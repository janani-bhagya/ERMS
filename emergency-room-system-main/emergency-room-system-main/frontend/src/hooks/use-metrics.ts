/**
 * Custom hook for managing metrics data
 * Provides easy access to performance metrics with automatic refresh
 */

import { useState, useEffect, useCallback } from 'react'
import { metricsAPI } from '@/lib/api'
import { AggregateMetrics, ESIMetrics, PatientMetrics } from '@/types/api'

interface UseMetricsOptions {
  hours?: number
  refreshInterval?: number // in milliseconds
  autoRefresh?: boolean
}

export function useMetrics(options: UseMetricsOptions = {}) {
  const {
    hours = 24,
    refreshInterval = 30000, // 30 seconds default
    autoRefresh = true,
  } = options

  const [aggregateMetrics, setAggregateMetrics] = useState<AggregateMetrics | null>(null)
  const [esiMetrics, setESIMetrics] = useState<ESIMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const [aggregateResponse, esiResponse] = await Promise.all([
        metricsAPI.getAggregateMetrics(hours),
        metricsAPI.getMetricsByESI(hours),
      ])

      setAggregateMetrics(aggregateResponse.data.statistics)
      setESIMetrics(esiResponse.data.metrics_by_esi_level)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics')
      setLoading(false)
    }
  }, [hours])

  useEffect(() => {
    fetchMetrics()

    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(fetchMetrics, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchMetrics, autoRefresh, refreshInterval])

  return {
    aggregateMetrics,
    esiMetrics,
    loading,
    error,
    refetch: fetchMetrics,
  }
}

export function usePatientMetrics(patientId: string | null) {
  const [metrics, setMetrics] = useState<PatientMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMetrics = useCallback(async () => {
    if (!patientId) return

    try {
      setLoading(true)
      setError(null)

      const response = await metricsAPI.getPatientMetrics(patientId)
      setMetrics(response.data.metrics)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch patient metrics')
      setLoading(false)
    }
  }, [patientId])

  useEffect(() => {
    fetchMetrics()
  }, [fetchMetrics])

  return {
    metrics,
    loading,
    error,
    refetch: fetchMetrics,
  }
}
