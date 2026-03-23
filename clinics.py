from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.auth import ClinicCreate
from app.models.clinic import Clinic
from app.core.dependencies import require_admin

router = APIRouter()

@router.post("")
def create_clinic(payload: ClinicCreate, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    if db.scalars(select(Clinic).where(Clinic.name == payload.name)).first():
        raise HTTPException(status_code=400, detail="Clinic already exists")
    clinic = Clinic(name=payload.name, plan=payload.plan)
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return {"id": clinic.id, "name": clinic.name, "plan": clinic.plan}

@router.get("")
def list_clinics(db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    clinics = db.scalars(select(Clinic).order_by(Clinic.created_at.desc())).all()
    return [{"id": c.id, "name": c.name, "plan": c.plan, "is_active": c.is_active} for c in clinics]
