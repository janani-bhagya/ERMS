export interface Patient {
  id: string
  name: string
  age: number
  esi_level: 1 | 2 | 3 | 4 | 5
  chief_complaint: string
  vital_signs: Record<string, any>
  status: 'waiting' | 'in_treatment' | 'discharged' | 'admitted'
  priority_score: number
  waiting_time: number
  created_at: string
  updated_at: string
}

export interface PatientCreate {
  name: string
  age: number
  esi_level: 1 | 2 | 3 | 4 | 5
  chief_complaint: string
  vital_signs: Record<string, any>
}

export interface TriageStatus {
  patients_waiting: number
  system_status: string
}

export interface Resource {
  id: string
  name: string
  type: 'room' | 'equipment' | 'staff'
  status: 'available' | 'in_use' | 'maintenance'
  utilization: number
  location?: string
}

export interface DashboardStats {
  totalPatients: number
  waitingPatients: number
  avgWaitTime: number
  resourceUtilization: number
}

export interface APIResponse<T> {
  data: T
  message: string
  success: boolean
}

// Metrics Types - NEW
export interface PatientMetrics {
  id: number
  patient_id: string
  arrival_time: string | null
  triage_complete_time: string | null
  provider_contact_time: string | null
  treatment_start_time: string | null
  discharge_time: string | null
  door_to_triage_minutes: number | null
  door_to_provider_minutes: number | null
  door_to_treatment_minutes: number | null
  length_of_stay_minutes: number | null
  esi_level: number | null
  chief_complaint: string | null
  created_at: string
  updated_at: string
}

export interface AggregateMetrics {
  total_patients: number
  avg_door_to_provider_minutes: number | null
  avg_length_of_stay_minutes: number | null
  avg_door_to_triage_minutes: number | null
  patients_with_complete_metrics: number
  time_window_hours: number
}

export interface ESIMetrics {
  [key: number]: {
    count: number
    avg_door_to_provider: number | null
  }
}

// Graph Types - NEW
export interface GraphEdge {
  from_vertex: string
  to_vertex: string
  weight: number
}

export interface GraphPath {
  from: string
  to: string
  path: string[]
  steps: number
}

export interface BFSResult {
  start: string
  max_depth: number | null
  resources_found: number
  resources_by_depth: Record<number, string[]>
  all_results: Array<{ resource: string; depth: number }>
}

export interface DFSResult {
  start: string
  end: string | null
  path: string[]
  steps: number
}

export interface BottleneckResource {
  resource: string
  connections: number
}

export interface BottlenecksResult {
  message: string
  total_resources: number
  bottlenecks: BottleneckResource[]
}

export interface ResourceConnections {
  resource: string
  connection_count: number
  neighbors: Array<{
    resource: string
    weight: number
  }>
}
