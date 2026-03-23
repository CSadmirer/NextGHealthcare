from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.appointment_service import create_appointment, list_appointments, update_appointment, cancel_appointment
from app.core.dependencies import require_staff

router = APIRouter()

@router.post("")
def create(payload: AppointmentCreate, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    appt = create_appointment(db, payload)
    return {"id": appt.id, "status": appt.status, "appointment_at": appt.appointment_at}

@router.get("")
def list_all(clinic_id: int, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    rows = list_appointments(db, clinic_id)
    return [
        {
            "id": a.id,
            "clinic_id": a.clinic_id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "reason": a.reason,
            "status": a.status,
            "appointment_at": a.appointment_at,
            "priority": a.priority,
            "notes": a.notes,
        }
        for a in rows
    ]

@router.patch("/{appointment_id}")
def update(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    a = update_appointment(db, appointment_id, payload)
    return {"id": a.id, "status": a.status, "appointment_at": a.appointment_at}

@router.delete("/{appointment_id}")
def cancel(appointment_id: int, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    a = cancel_appointment(db, appointment_id)
    return {"id": a.id, "status": a.status}
