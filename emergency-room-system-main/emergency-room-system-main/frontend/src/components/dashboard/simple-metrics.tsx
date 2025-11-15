/**
 * Simple Metrics Dashboard Component
 * Displays key ER performance metrics
 */

'use client';

import { Card } from '@/components/ui/card';
import { useMetrics } from '@/hooks/use-metrics';

export function SimpleMetrics() {
  const { aggregateMetrics, esiMetrics, loading, error, refetch } = useMetrics({
    hours: 24,
    refreshInterval: 30000,
    autoRefresh: true,
  });

  const formatMinutes = (minutes: number | null): string => {
    if (minutes === null) return 'N/A';
    if (minutes < 60) return `${minutes.toFixed(0)} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins.toFixed(0)}m`;
  };

  const getMetricColor = (minutes: number | null, target: number): string => {
    if (minutes === null) return 'text-gray-500';
    if (minutes <= target) return 'text-green-600';
    if (minutes <= target * 1.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Performance Metrics</h2>
        <Card className="p-6 border-red-200 bg-red-50">
          <p className="text-red-600">Error loading metrics: {error}</p>
          <button
            onClick={refetch}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </Card>
      </div>
    );
  }

  if (!aggregateMetrics) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Performance Metrics (Last 24 Hours)</h2>
        <button
          onClick={refetch}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Door-to-Provider Time */}
        <Card className="p-6">
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-600">
              Avg. Door-to-Provider Time
            </h3>
            <p
              className={`text-3xl font-bold ${getMetricColor(
                aggregateMetrics.avg_door_to_provider_minutes,
                45
              )}`}
            >
              {formatMinutes(aggregateMetrics.avg_door_to_provider_minutes)}
            </p>
            <p className="text-xs text-gray-500">Target: &lt;45 min</p>
          </div>
        </Card>

        {/* Length of Stay */}
        <Card className="p-6">
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-600">
              Avg. Length of Stay
            </h3>
            <p
              className={`text-3xl font-bold ${getMetricColor(
                aggregateMetrics.avg_length_of_stay_minutes,
                240
              )}`}
            >
              {formatMinutes(aggregateMetrics.avg_length_of_stay_minutes)}
            </p>
            <p className="text-xs text-gray-500">Target: &lt;4 hours</p>
          </div>
        </Card>

        {/* Patients Seen */}
        <Card className="p-6">
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-600">Patients Seen</h3>
            <p className="text-3xl font-bold text-blue-600">
              {aggregateMetrics.total_patients}
            </p>
            <p className="text-xs text-gray-500">
              {aggregateMetrics.patients_with_complete_metrics} discharged
            </p>
          </div>
        </Card>
      </div>

      {/* Door-to-Triage Time */}
      {aggregateMetrics.avg_door_to_triage_minutes !== null && (
        <Card className="p-6">
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-600">
              Avg. Door-to-Triage Time
            </h3>
            <p
              className={`text-2xl font-bold ${getMetricColor(
                aggregateMetrics.avg_door_to_triage_minutes,
                15
              )}`}
            >
              {formatMinutes(aggregateMetrics.avg_door_to_triage_minutes)}
            </p>
            <p className="text-xs text-gray-500">Target: &lt;15 min</p>
          </div>
        </Card>
      )}

      {/* ESI Level Breakdown */}
      {esiMetrics && Object.keys(esiMetrics).length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">
            Door-to-Provider Time by ESI Level
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[1, 2, 3, 4, 5].map((level) => {
              const data = esiMetrics[level];
              if (!data) return null;

              const getESITarget = (level: number): number => {
                if (level === 1) return 5;
                if (level === 2) return 10;
                if (level === 3) return 45;
                return 60;
              };

              return (
                <div key={level} className="border rounded p-4">
                  <div className="text-center">
                    <div
                      className={`text-xs font-semibold mb-1 ${
                        level === 1
                          ? 'text-red-600'
                          : level === 2
                          ? 'text-orange-600'
                          : level === 3
                          ? 'text-yellow-600'
                          : 'text-green-600'
                      }`}
                    >
                      ESI {level}
                    </div>
                    <div className="text-2xl font-bold">
                      {formatMinutes(data.avg_door_to_provider)}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {data.count} patients
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      Target: &lt;{getESITarget(level)}m
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Information Footer */}
      <div className="text-xs text-gray-500 text-center">
        Data refreshes automatically every 30 seconds. Times calculated from patient
        arrival to key milestones.
      </div>
    </div>
  );
}
