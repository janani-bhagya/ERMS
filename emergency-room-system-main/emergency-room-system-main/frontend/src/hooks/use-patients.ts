import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { patientAPI } from '@/lib/api'
import { Patient, PatientCreate } from '@/types/api'

export const usePatients = (status?: string) => {
  const queryClient = useQueryClient()
  
  const query = useQuery({
    queryKey: ['patients', status],
    queryFn: async () => {
      const response = await patientAPI.getPatients(status)
      return response.data.patients
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  const addPatientMutation = useMutation({
    mutationFn: (patient: PatientCreate) => patientAPI.addPatient(patient),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] })
    },
  })

  const dischargePatientMutation = useMutation({
    mutationFn: (patientId: string) => patientAPI.dischargePatient(patientId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] })
    },
  })

  const getNextPatientMutation = useMutation({
    mutationFn: () => patientAPI.getNextPatient(),
  })

  return {
    patients: query.data || [],
    isLoading: query.isLoading,
    error: query.error,
    addPatient: addPatientMutation.mutate,
    isAdding: addPatientMutation.isPending,
    dischargePatient: dischargePatientMutation.mutate,
    isDischarging: dischargePatientMutation.isPending,
    getNextPatient: getNextPatientMutation.mutate,
    nextPatient: getNextPatientMutation.data?.data,
  }
}

export const usePatient = (id: string) => {
  return useQuery({
    queryKey: ['patient', id],
    queryFn: () => patientAPI.getPatient(id).then(res => res.data),
    enabled: !!id,
  })
}