import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTime(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
}

export function getESILevelText(esi: number): string {
  const levels = {
    1: 'Resuscitation',
    2: 'Emergency',
    3: 'Urgent',
    4: 'Less Urgent',
    5: 'Non-Urgent'
  }
  return levels[esi as keyof typeof levels] || 'Unknown'
}

export function getESILevelColor(esi: number): string {
  const colors = {
    1: 'red',
    2: 'orange',
    3: 'yellow',
    4: 'green',
    5: 'blue'
  }
  return colors[esi as keyof typeof colors] || 'gray'
}

export function calculatePriorityScore(
  esi: number,
  waitingTime: number,
  vitalSigns: Record<string, any>
): number {
  let score = (6 - esi) * 20 // ESI contributes 20-100 points
  
  // Waiting time adjustment (max 20 points)
  score += Math.min(waitingTime * 0.5, 20)
  
  // Vital signs adjustments
  if (vitalSigns.heartRate && (vitalSigns.heartRate < 50 || vitalSigns.heartRate > 120)) {
    score += 10
  }
  
  if (vitalSigns.oxygenSaturation && vitalSigns.oxygenSaturation < 92) {
    score += 15
  }
  
  return Math.min(score, 100)
}