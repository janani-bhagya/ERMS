"""
Risk Scoring Service - Implements predictive analytics for patient deterioration risk
Addresses proposal Section 2.3: "predictive analytics for patient deterioration risk"

This service provides rule-based risk assessment using vital signs and clinical indicators.
While the proposal mentions ML-based prediction, this MVP implementation uses evidence-based
clinical thresholds as a foundation that could be enhanced with ML models in the future.
"""
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.patient import Patient


class RiskScoringService:
    """
    Calculate deterioration risk scores for patients based on vital signs and clinical indicators.
    
    Risk Score Components:
    - Vital Signs Thresholds (based on Early Warning Scores)
    - ESI Level (Emergency Severity Index)
    - Age Factor
    - Comorbidities
    
    Risk Levels:
    - CRITICAL (>80): Immediate intervention needed
    - HIGH (60-80): Close monitoring required
    - MODERATE (40-60): Standard monitoring
    - LOW (<40): Routine care
    """
    
    # Clinical thresholds based on Modified Early Warning Score (MEWS)
    VITAL_SIGNS_THRESHOLDS = {
        'heart_rate': {
            'critical_high': 130,
            'high': 120,
            'normal_high': 100,
            'normal_low': 60,
            'low': 50,
            'critical_low': 40
        },
        'blood_pressure_systolic': {
            'critical_high': 200,
            'high': 180,
            'normal_high': 140,
            'normal_low': 90,
            'low': 80,
            'critical_low': 70
        },
        'respiratory_rate': {
            'critical_high': 35,
            'high': 30,
            'normal_high': 20,
            'normal_low': 12,
            'low': 10,
            'critical_low': 8
        },
        'oxygen_saturation': {
            'critical_low': 85,
            'low': 90,
            'normal_low': 95,
            'normal_high': 100
        },
        'temperature': {
            'critical_high': 39.5,
            'high': 38.5,
            'normal_high': 37.5,
            'normal_low': 36.0,
            'low': 35.5,
            'critical_low': 35.0
        }
    }
    
    def calculate_risk_score(self, patient_data: Dict, db: Session) -> Dict:
        """
        Calculate comprehensive risk score for patient deterioration.
        
        Args:
            patient_data: Patient data including vital signs and demographics
            db: Database session
        
        Returns:
            Dict with risk_score (0-100), risk_level, risk_factors, and recommendations
        """
        risk_score = 0
        risk_factors = []
        recommendations = []
        
        # 1. Vital Signs Assessment (0-50 points)
        vital_score, vital_factors = self._assess_vital_signs(patient_data)
        risk_score += vital_score
        risk_factors.extend(vital_factors)
        
        # 2. ESI Level Weight (0-25 points)
        esi_score, esi_factors = self._assess_esi_level(patient_data)
        risk_score += esi_score
        risk_factors.extend(esi_factors)
        
        # 3. Age Factor (0-15 points)
        age_score, age_factors = self._assess_age_risk(patient_data)
        risk_score += age_score
        risk_factors.extend(age_factors)
        
        # 4. Comorbidities (0-10 points)
        comorbid_score, comorbid_factors = self._assess_comorbidities(patient_data)
        risk_score += comorbid_score
        risk_factors.extend(comorbid_factors)
        
        # Determine risk level and recommendations
        risk_level = self._determine_risk_level(risk_score)
        recommendations = self._generate_recommendations(risk_level, risk_factors)
        
        return {
            'risk_score': min(100, risk_score),  # Cap at 100
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _assess_vital_signs(self, patient_data: Dict) -> tuple[float, list]:
        """Assess vital signs against clinical thresholds (0-50 points)"""
        score = 0
        factors = []
        
        vital_signs = patient_data.get('vital_signs', {})
        
        # Heart Rate Assessment (0-12 points)
        hr = vital_signs.get('heart_rate')
        if hr:
            if hr >= self.VITAL_SIGNS_THRESHOLDS['heart_rate']['critical_high']:
                score += 12
                factors.append(f"Critical tachycardia (HR: {hr})")
            elif hr >= self.VITAL_SIGNS_THRESHOLDS['heart_rate']['high']:
                score += 8
                factors.append(f"Tachycardia (HR: {hr})")
            elif hr <= self.VITAL_SIGNS_THRESHOLDS['heart_rate']['critical_low']:
                score += 12
                factors.append(f"Critical bradycardia (HR: {hr})")
            elif hr <= self.VITAL_SIGNS_THRESHOLDS['heart_rate']['low']:
                score += 8
                factors.append(f"Bradycardia (HR: {hr})")
        
        # Blood Pressure Assessment (0-12 points)
        bp = vital_signs.get('blood_pressure_systolic')
        if bp:
            if bp >= self.VITAL_SIGNS_THRESHOLDS['blood_pressure_systolic']['critical_high']:
                score += 12
                factors.append(f"Hypertensive crisis (BP: {bp})")
            elif bp >= self.VITAL_SIGNS_THRESHOLDS['blood_pressure_systolic']['high']:
                score += 6
                factors.append(f"Hypertension (BP: {bp})")
            elif bp <= self.VITAL_SIGNS_THRESHOLDS['blood_pressure_systolic']['critical_low']:
                score += 12
                factors.append(f"Critical hypotension (BP: {bp})")
            elif bp <= self.VITAL_SIGNS_THRESHOLDS['blood_pressure_systolic']['low']:
                score += 8
                factors.append(f"Hypotension (BP: {bp})")
        
        # Respiratory Rate Assessment (0-10 points)
        rr = vital_signs.get('respiratory_rate')
        if rr:
            if rr >= self.VITAL_SIGNS_THRESHOLDS['respiratory_rate']['critical_high']:
                score += 10
                factors.append(f"Critical tachypnea (RR: {rr})")
            elif rr >= self.VITAL_SIGNS_THRESHOLDS['respiratory_rate']['high']:
                score += 6
                factors.append(f"Tachypnea (RR: {rr})")
            elif rr <= self.VITAL_SIGNS_THRESHOLDS['respiratory_rate']['critical_low']:
                score += 10
                factors.append(f"Critical bradypnea (RR: {rr})")
        
        # Oxygen Saturation Assessment (0-10 points)
        o2 = vital_signs.get('oxygen_saturation')
        if o2:
            if o2 <= self.VITAL_SIGNS_THRESHOLDS['oxygen_saturation']['critical_low']:
                score += 10
                factors.append(f"Critical hypoxia (O2: {o2}%)")
            elif o2 <= self.VITAL_SIGNS_THRESHOLDS['oxygen_saturation']['low']:
                score += 6
                factors.append(f"Hypoxia (O2: {o2}%)")
        
        # Temperature Assessment (0-6 points)
        temp = vital_signs.get('temperature')
        if temp:
            if temp >= self.VITAL_SIGNS_THRESHOLDS['temperature']['critical_high']:
                score += 6
                factors.append(f"High fever (Temp: {temp}°C)")
            elif temp <= self.VITAL_SIGNS_THRESHOLDS['temperature']['critical_low']:
                score += 6
                factors.append(f"Hypothermia (Temp: {temp}°C)")
        
        return score, factors
    
    def _assess_esi_level(self, patient_data: Dict) -> tuple[float, list]:
        """Assess Emergency Severity Index level (0-25 points)"""
        esi_level = patient_data.get('esi_level', 5)
        factors = []
        
        esi_scores = {
            1: (25, "ESI Level 1 - Immediate life-saving intervention required"),
            2: (20, "ESI Level 2 - High risk situation"),
            3: (12, "ESI Level 3 - Urgent but stable"),
            4: (5, "ESI Level 4 - Less urgent"),
            5: (0, "ESI Level 5 - Non-urgent")
        }
        
        score, factor = esi_scores.get(esi_level, (0, ""))
        if factor:
            factors.append(factor)
        
        return score, factors
    
    def _assess_age_risk(self, patient_data: Dict) -> tuple[float, list]:
        """Assess age-related risk factors (0-15 points)"""
        age = patient_data.get('age', 0)
        factors = []
        score = 0
        
        if age >= 80:
            score = 15
            factors.append("Advanced age (≥80 years) - high risk")
        elif age >= 65:
            score = 10
            factors.append("Elderly (65-79 years) - increased risk")
        elif age < 2:
            score = 12
            factors.append("Infant (<2 years) - vulnerable population")
        elif age < 18:
            score = 5
            factors.append("Pediatric patient - special considerations")
        
        return score, factors
    
    def _assess_comorbidities(self, patient_data: Dict) -> tuple[float, list]:
        """Assess comorbidity risk (0-10 points)"""
        medical_history = patient_data.get('medical_history', '')
        factors = []
        score = 0
        
        # High-risk conditions
        high_risk_conditions = [
            'heart failure', 'cardiac', 'copd', 'diabetes', 
            'renal failure', 'cancer', 'immunosuppressed'
        ]
        
        medical_history_lower = medical_history.lower()
        matched_conditions = [
            cond for cond in high_risk_conditions 
            if cond in medical_history_lower
        ]
        
        if matched_conditions:
            score = min(10, len(matched_conditions) * 3)
            factors.append(f"Significant comorbidities present: {', '.join(matched_conditions)}")
        
        return score, factors
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level category from score"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MODERATE"
        else:
            return "LOW"
    
    def _generate_recommendations(self, risk_level: str, risk_factors: list) -> list:
        """Generate clinical recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "Immediate physician evaluation required",
                "Consider ICU admission",
                "Continuous vital signs monitoring",
                "Prepare for potential deterioration"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "Priority physician assessment",
                "Frequent vital signs monitoring (every 15-30 minutes)",
                "Consider telemetry monitoring",
                "Notify senior staff"
            ])
        elif risk_level == "MODERATE":
            recommendations.extend([
                "Standard physician assessment",
                "Regular vital signs monitoring (every 1-2 hours)",
                "Monitor for changes in condition"
            ])
        else:
            recommendations.extend([
                "Routine monitoring",
                "Standard assessment procedures"
            ])
        
        # Specific recommendations based on risk factors
        for factor in risk_factors:
            if 'hypoxia' in factor.lower():
                recommendations.append("Administer supplemental oxygen as needed")
            if 'hypotension' in factor.lower():
                recommendations.append("Consider fluid resuscitation")
            if 'tachycardia' in factor.lower():
                recommendations.append("ECG monitoring recommended")
        
        return recommendations
    
    def update_patient_risk(self, patient_id: str, db: Session) -> Optional[Dict]:
        """
        Calculate and update risk score for a patient in the database.
        
        Args:
            patient_id: Patient identifier
            db: Database session
        
        Returns:
            Updated risk assessment or None if patient not found
        """
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return None
        
        # Extract vital signs with proper mapping
        vital_signs = patient.vital_signs or {}
        mapped_vitals = {
            'heart_rate': vital_signs.get('hr'),
            'blood_pressure_systolic': int(vital_signs.get('bp', '0/0').split('/')[0]) if vital_signs.get('bp') else None,
            'respiratory_rate': vital_signs.get('rr'),
            'oxygen_saturation': vital_signs.get('spo2'),
            'temperature': vital_signs.get('temp')
        }
        
        patient_data = {
            'esi_level': patient.esi_level,
            'age': patient.age,
            'vital_signs': mapped_vitals,
            'medical_history': patient.chief_complaint or ''  # Use chief complaint as proxy for medical history
        }
        
        risk_assessment = self.calculate_risk_score(patient_data, db)
        
        # Update patient record with new priority score if risk is high
        if risk_assessment['risk_level'] in ['CRITICAL', 'HIGH']:
            # Boost priority score for high-risk patients
            patient.priority_score = max(patient.priority_score, risk_assessment['risk_score'])
            db.commit()
        
        return risk_assessment
