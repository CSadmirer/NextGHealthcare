from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.patient import PatientCreate, PatientSearch
from app.services.patient_service import create_patient, list_patients, search_patients, get_patient
from app.core.dependencies import require_staff

router = APIRouter()

@router.post("")
def create(payload: PatientCreate, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    p = create_patient(db, payload)
    return {"id": p.id, "full_name": p.full_name, "clinic_id": p.clinic_id}

@router.get("")
def list_all(clinic_id: int, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    return list_patients(db, clinic_id)

@router.get("/search")
def search(q: str, clinic_id: int, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    return search_patients(db, clinic_id, q)

@router.get("/{patient_id}")
def get_one(patient_id: int, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    return get_patient(db, patient_id)
