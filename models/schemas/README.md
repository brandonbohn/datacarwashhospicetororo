# Tororo Hospice Data Models

**Version:** 1.0  
**Date:** January 15, 2025  
**Author:** Brandon Bohn  
**Purpose:** Core JSON schemas for the Tororo Hospice Management System

## Overview

This directory contains the **7 core JSON data models** for the hospice management system. These models are designed to be:

- ✅ **Flexible** - Handle multiple forms and use cases
- ✅ **Extensible** - Easy to add new fields without breaking existing data
- ✅ **Normalized** - Minimize data duplication
- ✅ **FHIR-inspired** - Follow international healthcare data standards
- ✅ **Simple** - Not over-complicated, practical for rural hospice use

---

## The 7 Core Models

### 1. **Person** (`person.json`)
**Purpose:** Universal model for anyone in the system

**Person Types:**
- Patients (receiving care)
- Staff (doctors, nurses, counselors)
- Caregivers (family members)
- Volunteers (community helpers)
- Community Health Workers (CHWs)
- Donors (financial supporters)
- Referral Contacts (other facilities)

**Key Concept:** One table for all people, with flexible `role_data` that changes based on `person_type`.

**Benefits:**
- Same person can have multiple roles (e.g., caregiver becomes patient)
- Centralized contact management
- Simplified relationships tracking

---

### 2. **Encounter** (`encounter.json`)
**Purpose:** ANY interaction with a patient

**Encounter Types:**
- Initial Assessment
- Follow-up Visit
- Home Visit
- Clinic Visit
- Phone Call
- Emergency Visit
- Medical Exam
- Medication Review
- Counseling Session
- Bereavement Visit

**Key Concept:** All Kobo forms feed into encounters with flexible `form_data` field.

**Benefits:**
- Single structure for all forms
- Timeline of all patient interactions
- Links to observations, treatments, notes created during encounter

---

### 3. **Medical_Record** (`medical_record.json`)
**Purpose:** Clinical history and documentation

**Record Types:**
- Diagnosis
- Clinical Note
- Progress Note
- Lab Result
- Imaging Report
- Patient History
- Physical Exam
- Discharge Summary
- Death Certificate

**Key Concept:** Flexible `content` field stores different types of clinical documentation.

**Benefits:**
- Comprehensive medical history
- Structured and unstructured notes
- Attachments support (encrypted files)

---

### 4. **Treatment** (`treatment.json`)
**Purpose:** ANY intervention given to patient

**Treatment Types:**
- Medication
- Procedure
- Counseling
- Education
- Equipment Provision
- Wound Care
- Spiritual Care
- Referral

**Key Concept:** Flexible `details` field stores treatment-specific information.

**Benefits:**
- Complete treatment history
- Track effectiveness and side effects
- Medication adherence monitoring

---

### 5. **Disease** (`disease.json`)
**Purpose:** Track diagnoses and medical conditions

**Disease Categories:**
- Cancer (primary use case)
- HIV/AIDS
- Diabetes
- Hypertension
- Tuberculosis
- Other chronic diseases

**Key Concept:** Flexible `disease_details` field stores disease-specific clinical data.

**Benefits:**
- Detailed cancer staging and tracking
- Comorbidity management
- Prognosis tracking

---

### 6. **Observation** (`observation.json`)
**Purpose:** Track changing clinical data over time

**Observation Types:**
- Symptoms (33+ symptoms from Kobo form!)
- Vital Signs
- Physical Measurements (weight, BMI)
- Pain Assessments
- Functional Assessments (Karnofsky, ECOG)
- Lab Values
- Assessment Scores (ESAS, etc.)

**Key Concept:** Time-series data for trending and monitoring.

**Benefits:**
- Track symptom changes over time
- Identify trends (improving/worsening)
- Support clinical decision-making

---

### 7. **Supply** (`supply.json`)
**Purpose:** Inventory management for all hospice supplies

**Supply Types:**
- Medications
- Medical Equipment
- Medical Consumables
- Office Supplies
- Personal Protective Equipment (PPE)
- Cleaning Supplies
- Nutrition Supplements
- Educational Materials

**Key Concept:** Complete supply chain tracking from procurement to patient dispensing.

**Features:**
- Batch tracking with expiration dates
- Transaction history (received, dispensed, adjusted)
- Low stock alerts and reorder points
- Controlled substance management
- Links to Treatment model when dispensed to patients
- Supplier and cost tracking
- Equipment loan tracking

**Benefits:**
- Prevent stockouts of critical medications
- Track controlled substances (morphine, etc.)
- Expiration date management
- Complete audit trail
- Cost control and budgeting
- Equipment accountability

---

## Data Flow

```
Kobo Form (Excel/CSV)
    ↓
Upload & Scan
    ↓
Normalization
    ↓
JSON Models Created:
    ├── Person (patient demographics)
    ├── Encounter (the visit/form submission)
    ├── Medical_Record (diagnosis, notes)
    ├── Disease (cancer diagnosis)
    ├── Treatment (medications prescribed)
    ├── Observation (33 symptoms assessed)
    └── Supply (medication stock updated)
    ↓
Save as JSON
    ↓
Encrypt to ZIP
    ↓
Secure Storage
```

---

## Inheritance & Relationships

### All models inherit from BaseModel:
```json
{
  "id": "uuid",
  "created_at": "timestamp",
  "created_by": "staff_id",
  "updated_at": "timestamp",
  "updated_by": "staff_id",
  "is_deleted": false,
  "metadata": {}
}
```

### Relationships:
```
Person (patient)
    ├── has many Encounters
    ├── has many Diseases
    ├── has many Treatments
    └── has many Observations

Encounter
    ├── belongs to Person
    ├── creates Medical_Records
    ├── creates Treatments
    └── creates Observations

Disease
    ├── belongs to Person
    └── documented in Medical_Record

Treatment
    ├── belongs to Person
    ├── prescribed during Encounter
    └── links to Supply (when medication dispensed)

Observation
    ├── belongs to Person
    └── recorded during Encounter

Supply
    ├── tracks inventory for all items
    ├── links to Treatment (when dispensed to patient)
    └── maintains transaction history
```
    ├── belongs to Person
    └── recorded during Encounter
```

---

## Field Naming Conventions

1. **snake_case** for all field names
2. **_options** suffix for enums/choices (e.g., `status_options`)
3. **_id** suffix for foreign keys (e.g., `patient_id`)
4. **_date** suffix for dates (e.g., `created_date`)
5. **_datetime** suffix for timestamps (e.g., `recorded_datetime`)
6. **is_** prefix for booleans (e.g., `is_active`)

---

## Common Patterns

### Flexible Data Fields
Use flexible objects for varying structures:
- `role_data` in Person
- `form_data` in Encounter
- `content` in Medical_Record
- `details` in Treatment
- `disease_details` in Disease
- `value` in Observation

### Status Tracking
Most models include:
- `status` field with defined options
- `created_at` / `updated_at` timestamps
- `created_by` / `updated_by` staff references
- `is_deleted` for soft deletes

### Metadata
All models include `metadata` object for:
- Data source tracking
- Version control
- Import/export tracking
- System flags

---

## Usage Examples

### Creating a Patient from Kobo Intake Form:

```python
# Person model
{
  "person_id": "uuid-123",
  "person_type": "patient",
  "name": "john doe",
  "age": 45,
  "sex": "male",
  "role_data": {
    "registration_number": "REG-2025-0004",
    "enrollment_date": "2025-01-15"
  }
}

# Encounter model (initial assessment)
{
  "encounter_id": "uuid-456",
  "patient_id": "uuid-123",
  "encounter_type": "initial_assessment",
  "form_data": {
    # Full Kobo form data here
  }
}

# Disease model (cancer diagnosis)
{
  "disease_id": "uuid-789",
  "patient_id": "uuid-123",
  "disease_category": "cancer",
  "disease_name": "lung_cancer"
}

# 33 Observation models (one per symptom)
{
  "observation_id": "uuid-001",
  "patient_id": "uuid-123",
  "encounter_id": "uuid-456",
  "observation_type": "symptom",
  "observation_name": "anorexia",
  "value": {
    "severity": "moderate"
  }
}
```

---

## Next Steps

1. **Build Normalization Functions** - Convert Kobo CSV → these JSON models
2. **Create Database Schema** - SQLAlchemy models based on these JSONs
3. **Build API Endpoints** - CRUD operations for each model
4. **Implement Encryption** - Secure sensitive patient data
5. **Create Frontend** - Staff portal to manage data

---

## Notes

- ✅ These schemas are saved in this directory as reference
- ✅ Never lost again (backed up to GitHub!)
- ✅ Can be used to generate database migrations
- ✅ Can be used for API documentation
- ✅ Can be used for frontend form generation

---

## Questions?

Contact: Brandon Bohn  
Project: Tororo Hospice Management System  
Repository: github.com/brandonbohn/datacarwashhospicetororo
