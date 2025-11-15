import { create } from 'zustand'
import { Patient, TriageStatus, Resource, DashboardStats } from '@/types/api'

interface AppState {
  // Patients state
  patients: Patient[]
  currentPatient: Patient | null
  triageStatus: TriageStatus | null
  
  // Resources state
  resources: Resource[]
  resourceUtilization: number
  
  // Dashboard state
  dashboardStats: DashboardStats | null
  
  // Actions
  setPatients: (patients: Patient[]) => void
  addPatient: (patient: Patient) => void
  updatePatient: (id: string, updates: Partial<Patient>) => void
  removePatient: (id: string) => void
  setCurrentPatient: (patient: Patient | null) => void
  setTriageStatus: (status: TriageStatus) => void
  setResources: (resources: Resource[]) => void
  setDashboardStats: (stats: DashboardStats) => void
  
  // Computed
  waitingPatients: () => Patient[]
  inTreatmentPatients: () => Patient[]
  highPriorityPatients: () => Patient[]
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  patients: [],
  currentPatient: null,
  triageStatus: null,
  resources: [],
  resourceUtilization: 0,
  dashboardStats: null,

  // Actions
  setPatients: (patients) => set({ patients }),
  
  addPatient: (patient) => set((state) => ({ 
    patients: [...state.patients, patient] 
  })),
  
  updatePatient: (id, updates) => set((state) => ({
    patients: state.patients.map(patient =>
      patient.id === id ? { ...patient, ...updates } : patient
    )
  })),
  
  removePatient: (id) => set((state) => ({
    patients: state.patients.filter(patient => patient.id !== id)
  })),
  
  setCurrentPatient: (patient) => set({ currentPatient: patient }),
  
  setTriageStatus: (status) => set({ triageStatus: status }),
  
  setResources: (resources) => set({ resources }),
  
  setDashboardStats: (stats) => set({ dashboardStats: stats }),

  // Computed values
  waitingPatients: () => get().patients.filter(p => p.status === 'waiting'),
  inTreatmentPatients: () => get().patients.filter(p => p.status === 'in_treatment'),
  highPriorityPatients: () => get().patients.filter(p => p.priority_score >= 80),
}))