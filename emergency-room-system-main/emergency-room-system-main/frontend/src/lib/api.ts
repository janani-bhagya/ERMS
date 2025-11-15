import axios from 'axios'
import { Patient, PatientCreate, TriageStatus, Resource, DashboardStats } from '@/types/api'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const patientAPI = {
  // Get all patients
  getPatients: (status?: string) => 
    api.get<{ patients: Patient[]; count: number }>('/patients', { params: { status } }),
  
  // Add new patient
  addPatient: (patient: PatientCreate) => 
    api.post<{ patient_id: string; priority_score: number; message: string }>('/patients', patient),
  
  // Get next patient in queue
  getNextPatient: () => api.get<{
    patient_id: string
    priority: number
    clinical_data: any
  }>('/patients/triage/next'),
  
  // Get patient by ID
  getPatient: (id: string) => api.get<Patient>(`/patients/${id}`),
  
  // Start treatment for a patient (requires room and provider allocation)
  startTreatment: (id: string) => 
    api.put<{ 
      message: string; 
      patient_id: string; 
      status: string;
      room?: string;
      providers?: string[];
      summary?: string;
    }>(`/patients/${id}/start-treatment`),
  
  // Discharge patient
  dischargePatient: (id: string) => api.delete(`/patients/${id}/discharge`),
}

export const triageAPI = {
  // Get triage status
  getStatus: () => api.get<TriageStatus>('/triage/status'),
}

export const resourceAPI = {
  // Get all rooms
  getRooms: (includeOccupied: boolean = true) => 
    api.get('/rooms', { params: { include_occupied: includeOccupied } }),
  
  // Get all providers
  getProviders: (includeBusy: boolean = true) =>
    api.get('/providers', { params: { include_busy: includeBusy } }),
  
  // Get available rooms only
  getAvailableRooms: () =>
    api.get('/rooms', { params: { include_occupied: false } }),
  
  // Get available providers only
  getAvailableProviders: () =>
    api.get('/providers', { params: { include_busy: false } }),
  
  // Allocate resources (room + providers) to a patient
  allocateResources: (patientId: string, roomId: string, providerIds: string[]) =>
    api.post('/resources/allocate', providerIds, {
      params: { patient_id: patientId, room_id: roomId }
    }),
  
  // Get resource utilization metrics
  getUtilization: () =>
    api.get('/utilization'),
}

export const dashboardAPI = {
  // Get resource utilization metrics
  getMetrics: () => api.get<any>('/metrics/resource-utilization'),
}

export const treatmentAPI = {
  // Add treatment action
  addAction: (patientId: string, action: any) => 
    api.post('/treatments', { patient_id: patientId, ...action }),
  
  // Undo last action
  undoAction: (patientId: string) => 
    api.delete('/treatments/undo', { data: { patient_id: patientId } }),
  
  // Get treatment history
  getHistory: (patientId: string, includeUndone = false) => 
    api.get(`/treatments/${patientId}/history`, { params: { include_undone: includeUndone } }),
}

// Metrics API - NEW
export const metricsAPI = {
  // Record a timestamp milestone for a patient
  recordMilestone: (patientId: string, milestone: string, esiLevel?: number, chiefComplaint?: string) =>
    api.post('/api/metrics/record', {
      patient_id: patientId,
      milestone,
      esi_level: esiLevel,
      chief_complaint: chiefComplaint,
    }),

  // Get metrics for a specific patient
  getPatientMetrics: (patientId: string) =>
    api.get(`/api/metrics/patient/${patientId}`),

  // Get aggregate metrics for a time window
  getAggregateMetrics: (hours: number = 24) =>
    api.get('/api/metrics/aggregate', { params: { hours } }),

  // Get metrics grouped by ESI level
  getMetricsByESI: (hours: number = 24) =>
    api.get('/api/metrics/by-esi-level', { params: { hours } }),
}

// Graph API - NEW
export const graphAPI = {
  // Initialize graph with edges
  initGraph: (edges: Array<{ from_vertex: string; to_vertex: string; weight: number }>) =>
    api.post('/api/graph/init', { edges }),

  // Find shortest path between two resources
  getShortestPath: (fromVertex: string, toVertex: string) =>
    api.get('/api/graph/shortest-path', { params: { from_vertex: fromVertex, to_vertex: toVertex } }),

  // Perform breadth-first search
  bfs: (startVertex: string, maxDepth?: number) =>
    api.get('/api/graph/bfs', { params: { start_vertex: startVertex, max_depth: maxDepth } }),

  // Perform depth-first search
  dfs: (startVertex: string, endVertex?: string) =>
    api.get('/api/graph/dfs', { params: { start_vertex: startVertex, end_vertex: endVertex } }),

  // Find bottleneck resources
  getBottlenecks: () =>
    api.get('/api/graph/bottlenecks'),

  // List all vertices in the graph
  getVertices: () =>
    api.get('/api/graph/vertices'),

  // Get connections for a specific resource
  getResourceConnections: (vertex: string) =>
    api.get(`/api/graph/resource/${vertex}/connections`),
}

export default api