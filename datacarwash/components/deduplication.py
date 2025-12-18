"""
Deduplication component with smart merge logic.
- Personal info: UPDATE existing
- Encounters/visits: CREATE new (never duplicate)
- Observations: CREATE new (time-series data)
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def load_existing_records(json_path: Path) -> List[Dict]:
    """Load existing JSON records if file exists."""
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def find_duplicate_person(person: Dict, existing_persons: List[Dict]) -> Optional[Dict]:
    """
    Find duplicate person based on matching criteria.
    
    Returns:
        Existing person dict if found, None otherwise
    """
    name = person.get('name', '').lower().strip()
    reg_number = person.get('role_data', {}).get('registration_number', '').upper().strip()
    
    for existing in existing_persons:
        existing_name = existing.get('name', '').lower().strip()
        existing_reg = existing.get('role_data', {}).get('registration_number', '').upper().strip()
        
        # Match by registration number (strongest identifier)
        if reg_number and existing_reg and reg_number == existing_reg:
            return existing
        
        # Match by name + village + age (weaker but useful)
        if name and existing_name and name == existing_name:
            existing_village = existing.get('address', {}).get('village', '').lower().strip()
            new_village = person.get('address', {}).get('village', '').lower().strip()
            existing_age = existing.get('age')
            new_age = person.get('age')
            
            if existing_village == new_village and existing_age == new_age:
                return existing
    
    return None


def update_person_info(existing: Dict, new: Dict) -> Dict:
    """
    Update existing person with new information.
    Only updates if new data is more complete or different.
    """
    updated = existing.copy()
    
    # Update contact if new data exists
    if new.get('contact', {}).get('phone_primary'):
        updated['contact']['phone_primary'] = new['contact']['phone_primary']
    if new.get('contact', {}).get('phone_secondary'):
        updated['contact']['phone_secondary'] = new['contact']['phone_secondary']
    
    # Update address if more complete
    if new.get('address', {}).get('village'):
        updated['address']['village'] = new['address']['village']
    if new.get('address', {}).get('subcounty'):
        updated['address']['subcounty'] = new['address']['subcounty']
    if new.get('address', {}).get('district'):
        updated['address']['district'] = new['address']['district']
    
    # Update age if changed
    if new.get('age') and new['age'] != existing.get('age'):
        updated['age'] = new['age']
    
    # Update role_data
    if new.get('role_data'):
        if 'role_data' not in updated:
            updated['role_data'] = {}
        updated['role_data'].update(new['role_data'])
    
    # Update timestamp
    updated['updated_at'] = datetime.now().isoformat()
    
    return updated


def deduplicate_persons(new_persons: List[Dict], existing_persons: List[Dict]) -> Tuple[List[Dict], Dict[str, str]]:
    """
    Deduplicate person records with smart update logic.
    
    Returns:
        Tuple of (unique_persons, id_mapping)
        - unique_persons: New persons to add
        - id_mapping: Maps new_person_id -> existing_person_id for duplicates
    """
    unique_persons = []
    id_mapping = {}  # new_id -> existing_id
    updated_persons = []
    duplicate_count = 0
    
    for person in new_persons:
        existing = find_duplicate_person(person, existing_persons)
        
        if existing:
            # DUPLICATE FOUND - Update info, map IDs
            duplicate_count += 1
            id_mapping[person['person_id']] = existing['person_id']
            
            # Update existing person with new info
            updated = update_person_info(existing, person)
            updated_persons.append(updated)
            
            print(f"⚠️  Duplicate found: {person['name']} - updating info, will create new encounter")
        else:
            # NEW PERSON
            unique_persons.append(person)
    
    # Update existing persons list with updates
    for updated in updated_persons:
        for i, existing in enumerate(existing_persons):
            if existing['person_id'] == updated['person_id']:
                existing_persons[i] = updated
                break
    
    if duplicate_count > 0:
        print(f"✅ Updated {duplicate_count} existing person records")
    
    return unique_persons, id_mapping


def remap_ids(records: List[Dict], id_mapping: Dict[str, str], field_name: str = 'patient_id'):
    """
    Remap IDs in related records (encounters, observations, etc.)
    
    Args:
        records: List of records to update
        id_mapping: Dictionary mapping new_id -> existing_id
        field_name: Name of field to remap (patient_id, person_id, etc.)
    """
    for record in records:
        if record.get(field_name) in id_mapping:
            old_id = record[field_name]
            record[field_name] = id_mapping[old_id]


def save_with_deduplication(
    persons: List[Dict],
    encounters: List[Dict],
    observations: List[Dict],
    treatments: List[Dict],
    diseases: List[Dict],
    medical_records: List[Dict],
    output_path: Path
):
    """
    Save all records with smart deduplication:
    - Persons: UPDATE if duplicate
    - Encounters: Always CREATE (new visit)
    - Observations: Always CREATE (time-series)
    - Treatments: Always CREATE (new prescriptions)
    - Diseases: CREATE if different diagnosis
    - Medical_Records: Always CREATE (new notes)
    """
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load existing records
    existing_persons = load_existing_records(output_path / "persons.json")
    existing_encounters = load_existing_records(output_path / "encounters.json")
    existing_observations = load_existing_records(output_path / "observations.json")
    existing_treatments = load_existing_records(output_path / "treatments.json")
    existing_diseases = load_existing_records(output_path / "diseases.json")
    existing_medical_records = load_existing_records(output_path / "medical_records.json")
    
    # Deduplicate persons and get ID mapping
    unique_persons, id_mapping = deduplicate_persons(persons, existing_persons)
    
    # Remap IDs in related records
    if id_mapping:
        print(f"🔗 Remapping IDs for {len(id_mapping)} duplicate persons...")
        remap_ids(encounters, id_mapping, 'patient_id')
        remap_ids(observations, id_mapping, 'patient_id')
        remap_ids(treatments, id_mapping, 'patient_id')
        remap_ids(diseases, id_mapping, 'patient_id')
        remap_ids(medical_records, id_mapping, 'patient_id')
    
    # Merge: Persons (only unique ones - duplicates already updated in existing_persons)
    all_persons = existing_persons + unique_persons
    
    # Merge: Everything else (always append - these are time-series/events)
    all_encounters = existing_encounters + encounters
    all_observations = existing_observations + observations
    all_treatments = existing_treatments + treatments
    all_diseases = existing_diseases + diseases
    all_medical_records = existing_medical_records + medical_records
    
    # Save all files
    with open(output_path / "persons.json", 'w', encoding='utf-8') as f:
        json.dump(all_persons, f, indent=2, ensure_ascii=False)
    
    with open(output_path / "encounters.json", 'w', encoding='utf-8') as f:
        json.dump(all_encounters, f, indent=2, ensure_ascii=False)
    
    with open(output_path / "observations.json", 'w', encoding='utf-8') as f:
        json.dump(all_observations, f, indent=2, ensure_ascii=False)
    
    with open(output_path / "treatments.json", 'w', encoding='utf-8') as f:
        json.dump(all_treatments, f, indent=2, ensure_ascii=False)
    
    with open(output_path / "diseases.json", 'w', encoding='utf-8') as f:
        json.dump(all_diseases, f, indent=2, ensure_ascii=False)
    
    with open(output_path / "medical_records.json", 'w', encoding='utf-8') as f:
        json.dump(all_medical_records, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Persons: {len(unique_persons)} new, {len(id_mapping)} updated (total: {len(all_persons)})")
    print(f"   Encounters: {len(encounters)} new (total: {len(all_encounters)})")
    print(f"   Observations: {len(observations)} new (total: {len(all_observations)})")
    print(f"   Treatments: {len(treatments)} new (total: {len(all_treatments)})")
    print(f"   Diseases: {len(diseases)} new (total: {len(all_diseases)})")
    print(f"   Medical Records: {len(medical_records)} new (total: {len(all_medical_records)})")
