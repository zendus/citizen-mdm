from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import json
import logging
from collections import Counter
from datetime import datetime
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='mdm.log'
)

app = FastAPI(title="Citizen MDM Service")

# Pydantic models for data validation
class CitizenBase(BaseModel):
    citizen_id: str
    name: str
    dob: str
    gender: str

class HealthCitizen(CitizenBase):
    health_status: str

class EducationCitizen(CitizenBase):
    school_name: str

class MergedCitizen(CitizenBase):
    health_status: Optional[str] = None
    school_name: Optional[str] = None

# In-memory storage
merged_citizens: Dict[str, MergedCitizen] = {}

def resolve_value_conflicts(values: list) -> str:
    """
    Resolve conflicts by:
    1. Removing empty values (None, empty string, or whitespace-only strings)
    2. Taking most frequent non-empty value
    3. If all values are empty, return None
    """
    # Filter out None, empty strings, and whitespace-only strings
    valid_values = [v for v in values if v is not None and str(v).strip()]
    
    if not valid_values:
        return None
    
    # If only one valid value exists, return it
    if len(valid_values) == 1:
        return valid_values[0]
    
    # Get the most frequent value
    return Counter(valid_values).most_common(1)[0][0]

def load_data():
    """Load and merge data from both sources"""
    try:
        # Load health data
        with open('health.json', 'r') as f:
            health_data = json.load(f)['citizens']
        
        # Load education data
        with open('education.json', 'r') as f:
            education_data = json.load(f)['citizens']
        
        # Process and merge records
        all_records = {}
        
        # Process health records
        for record in health_data:
            citizen_id = record['citizen_id']
            if citizen_id not in all_records:
                all_records[citizen_id] = {
                    'names': [record.get('name')],  # Using get() to handle missing keys
                    'dobs': [record.get('dob')],
                    'genders': [record.get('gender')],
                    'health_status': record.get('health_status'),
                    'school_name': None
                }
        
        # Process education records
        for record in education_data:
            citizen_id = record['citizen_id']
            if citizen_id not in all_records:
                all_records[citizen_id] = {
                    'names': [record.get('name')],
                    'dobs': [record.get('dob')],
                    'genders': [record.get('gender')],
                    'health_status': None,
                    'school_name': record.get('school_name')
                }
            else:
                all_records[citizen_id]['names'].append(record.get('name'))
                all_records[citizen_id]['dobs'].append(record.get('dob'))
                all_records[citizen_id]['genders'].append(record.get('gender'))
                all_records[citizen_id]['school_name'] = record.get('school_name')
        
        # Resolve conflicts and create final records
        for citizen_id, data in all_records.items():
            # Resolve conflicts handling empty values
            name = resolve_value_conflicts(data['names'])
            dob = resolve_value_conflicts(data['dobs'])
            gender = resolve_value_conflicts(data['genders'])
            
            # Log any resolutions involving multiple non-empty values
            if len([n for n in data['names'] if n is not None and str(n).strip()]) > 1:
                logging.info(f"Name conflict resolved for citizen {citizen_id}: {data['names']} -> {name}")
            
            # Only create record if we have the minimum required data
            if name and dob and gender:
                merged_citizens[citizen_id] = MergedCitizen(
                    citizen_id=citizen_id,
                    name=name,
                    dob=dob,
                    gender=gender,
                    health_status=data['health_status'],
                    school_name=data['school_name']
                )
            else:
                logging.warning(f"Insufficient data for citizen {citizen_id}. Record skipped.")
        
        logging.info(f"Data loaded successfully. Total records: {len(merged_citizens)}")
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    """Load data when the application starts"""
    load_data()

@app.get("/citizens/{citizen_id}", response_model=MergedCitizen)
async def get_citizen(citizen_id: str):
    """Get a citizen record by ID"""
    if citizen_id not in merged_citizens:
        raise HTTPException(status_code=404, detail="Citizen not found")
    return merged_citizens[citizen_id]

@app.get("/citizens", response_model=List[MergedCitizen])
async def list_citizens():
    """List all citizen records"""
    return list(merged_citizens.values())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}