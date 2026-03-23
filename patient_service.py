from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.models.patient import Patient
from app.core.encryption import cipher

def create_patient(db: Session, payload):
    patient = Patient(
        clinic_id=payload.clinic_id,
        full_name=payload.full_name,
        phone_enc=cipher.encrypt(payload.phone),
        email_enc=cipher.encrypt(str(payload.email) if payload.email else None),
        age=payload.age,
        gender=payload.gender,
        history_enc=cipher.encrypt(payload.history),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def _as_dict(p: Patient):
    return {
        "id": p.id,
        "clinic_id": p.clinic_id,
        "full_name": p.full_name,
        "phone": cipher.decrypt(p.phone_enc),
        "email": cipher.decrypt(p.email_enc),
        "age": p.age,
        "gender": p.gender,
        "history": cipher.decrypt(p.history_enc),
        "created_at": p.created_at.isoformat(),
    }

def list_patients(db: Session, clinic_id: int):
    rows = db.scalars(select(Patient).where(Patient.clinic_id == clinic_id).order_by(Patient.created_at.desc())).all()
    return [_as_dict(p) for p in rows]

def search_patients(db: Session, clinic_id: int, query: str):
    rows = db.scalars(
        select(Patient).where(Patient.clinic_id == clinic_id, Patient.full_name.ilike(f"%{query}%")).order_by(Patient.full_name.asc())
    ).all()
    return [_as_dict(p) for p in rows]

def get_patient(db: Session, patient_id: int):
    p = db.get(Patient, patient_id)
    return _as_dict(p) if p else None
