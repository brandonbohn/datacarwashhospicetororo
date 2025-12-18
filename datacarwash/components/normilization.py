from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import uuid
from typing import Dict, List, Optional
from .deduplication import save_with_deduplication


def normalization(input_path: Path, output_path: Path) -> Path:
    """
    Convert Kobo Excel/CSV to separate JSON model files.
    
    Args:
        input_path: Path to Excel/CSV file
        output_path: Directory where JSON files will be saved
        
    Returns:
        Path to output directory
    """
    
    # Step 1: Read the file
    if input_path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(input_path)
    elif input_path.suffix == '.csv':
        df = pd.read_csv(input_path)
    else:
        raise ValueError(f"Unsupported file type: {input_path.suffix}")
    
    # Step 2: Initialize empty lists for each model
    persons = []
    encounters = []
    observations = []
    treatments = []
    diseases = []
    medical_records = []
    
    # Step 3: Loop through rows and SORT data into categories
    for index, row in df.iterrows():
        
        # Generate unique IDs
        person_id = str(uuid.uuid4())
        encounter_id = str(uuid.uuid4())
        
        # CATEGORY 1: Person (demographics)
        person = {
            "person_id": person_id,
            "person_type": "patient",
            "name": str(row.get('patient_name', '')).strip().lower() if pd.notna(row.get('patient_name')) else None,
            "age": int(row.get('age')) if pd.notna(row.get('age')) else None,
            "sex": str(row.get('sex', '')).strip().lower() if pd.notna(row.get('sex')) else None,
            "contact": {
                "phone_primary": row.get('phone') if pd.notna(row.get('phone')) else None,
                "phone_secondary": None
            },
            "address": {
                "village": str(row.get('village', '')).strip().lower() if pd.notna(row.get('village')) else None,
                "subcounty": None,
                "district": "tororo",
                "country": "uganda"
            },
            "role_data": {
                "registration_number": str(row.get('reg_number', '')).strip().upper() if pd.notna(row.get('reg_number')) else None,
                "enrollment_date": str(row.get('assessment_date', datetime.now().date())),
                "status": "active"
            },
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        persons.append(person)
        
        # CATEGORY 2: Encounter (visit/assessment)
        encounter = {
            "encounter_id": encounter_id,
            "patient_id": person_id,
            "encounter_type": "clinical_assessment",
            "encounter_date": str(row.get('assessment_date', datetime.now().date())),
            "encounter_time": None,
            "duration_minutes": None,
            "staff_id": None,
            "location_type": "clinic",
            "location_details": None,
            "chief_complaint": str(row.get('diagnosis', '')).strip() if pd.notna(row.get('diagnosis')) else None,
            "assessment_summary": str(row.get('summary', '')).strip() if pd.notna(row.get('summary')) else None,
            "plan": str(row.get('next_review', '')).strip() if pd.notna(row.get('next_review')) else None,
            "next_visit_date": str(row.get('next_review', '')).strip() if pd.notna(row.get('next_review')) else None,
            "status": "completed",
            "form_data": row.to_dict(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        encounters.append(encounter)
        
        # CATEGORY 3: Observations (vitals and physical exam)
        # Vital signs - combine into one observation
        vitals = {}
        if pd.notna(row.get('pulse_rate')):
            vitals['heart_rate'] = int(row['pulse_rate'])
        if pd.notna(row.get('bp_systol')):
            vitals['blood_pressure_systolic'] = int(row['bp_systol'])
        if pd.notna(row.get('bp_diastol')):
            vitals['blood_pressure_diastolic'] = int(row['bp_diastol'])
        if pd.notna(row.get('temperature')):
            vitals['temperature'] = float(row['temperature'])
        if pd.notna(row.get('resp_rate')):
            vitals['respiratory_rate'] = int(row['resp_rate'])
        
        if vitals:
            observations.append({
                "observation_id": str(uuid.uuid4()),
                "patient_id": person_id,
                "encounter_id": encounter_id,
                "observation_type": "vital_sign",
                "observation_category": "cardiovascular",
                "observation_name": "vital_signs",
                "value": vitals,
                "observation_date": encounter['encounter_date'],
                "recorded_by": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        # Physical exam findings - one observation per finding
        exam_fields = {
            'general_assessment': 'general',
            'cachexia': 'general',
            'jaundice': 'general',
            'pallor': 'general',
            'body_wasting': 'general'
        }
        
        for field, category in exam_fields.items():
            if pd.notna(row.get(field)):
                observations.append({
                    "observation_id": str(uuid.uuid4()),
                    "patient_id": person_id,
                    "encounter_id": encounter_id,
                    "observation_type": "physical_exam_finding",
                    "observation_category": category,
                    "observation_name": field,
                    "value": {"finding": str(row[field])},
                    "observation_date": encounter['encounter_date'],
                    "recorded_by": None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                })
        
        # Level of consciousness and orientation
        if pd.notna(row.get('loc')):
            observations.append({
                "observation_id": str(uuid.uuid4()),
                "patient_id": person_id,
                "encounter_id": encounter_id,
                "observation_type": "assessment_score",
                "observation_category": "neurological",
                "observation_name": "level_of_consciousness",
                "value": {"level": str(row['loc'])},
                "observation_date": encounter['encounter_date'],
                "recorded_by": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        if pd.notna(row.get('orientation')):
            observations.append({
                "observation_id": str(uuid.uuid4()),
                "patient_id": person_id,
                "encounter_id": encounter_id,
                "observation_type": "assessment_score",
                "observation_category": "neurological",
                "observation_name": "orientation",
                "value": {"status": str(row['orientation'])},
                "observation_date": encounter['encounter_date'],
                "recorded_by": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        # CATEGORY 4: Disease (diagnosis)
        if pd.notna(row.get('diagnosis')):
            diseases.append({
                "disease_id": str(uuid.uuid4()),
                "patient_id": person_id,
                "medical_record_id": None,
                "encounter_id": encounter_id,
                "disease_category": "unspecified",
                "disease_name": str(row['diagnosis']).strip().lower(),
                "icd10_code": None,
                "disease_details": {},
                "diagnosis_date": encounter['encounter_date'],
                "diagnosed_by": None,
                "status": "active",
                "severity": None,
                "prognosis": None,
                "notes": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        # CATEGORY 5: Treatments (medications)
        # Note: Repeating groups would need separate handling
        # For now, check if medication fields exist
        if pd.notna(row.get('med_name')):
            treatments.append({
                "treatment_id": str(uuid.uuid4()),
                "patient_id": person_id,
                "encounter_id": encounter_id,
                "treatment_type": "medication",
                "treatment_name": str(row['med_name']).strip(),
                "treatment_category": "symptom_control",
                "details": {
                    "generic_name": str(row['med_name']).strip(),
                    "dosage": str(row.get('dose', '')).strip() if pd.notna(row.get('dose')) else None,
                    "indication": str(row.get('indication', '')).strip() if pd.notna(row.get('indication')) else None
                },
                "start_date": encounter['encounter_date'],
                "end_date": str(row.get('date_completed', '')).strip() if pd.notna(row.get('date_completed')) else None,
                "status": "active",
                "notes": str(row.get('note_physician', '')).strip() if pd.notna(row.get('note_physician')) else None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        # CATEGORY 6: Medical Records (clinical notes)
        if pd.notna(row.get('summary')):
            medical_records.append({
                "record_id": str(uuid.uuid4()),
                "patient_id": person_id,
                "encounter_id": encounter_id,
                "record_type": "clinical_note",
                "record_date": encounter['encounter_date'],
                "record_time": None,
                "title": "Assessment Summary",
                "summary": str(row['summary']).strip(),
                "content": {
                    "note": str(row['summary']).strip(),
                    "seen_by": str(row.get('seen_by', '')).strip() if pd.notna(row.get('seen_by')) else None
                },
                "author_id": None,
                "status": "final",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
    
    # Step 4 & 5: Save with smart deduplication
    save_with_deduplication(
        persons=persons,
        encounters=encounters,
        observations=observations,
        treatments=treatments,
        diseases=diseases,
        medical_records=medical_records,
        output_path=output_path
    )
    
    return output_path