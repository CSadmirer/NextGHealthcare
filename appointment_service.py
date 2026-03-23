from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from app.models.appointment import Appointment
from app.models.patient import Patient

def _ensure_patient(db: Session, clinic_id: int, patient_id: int):
    patient = db.get(Patient, patient_id)
    if not patient or patient.clinic_id != clinic_id:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

def create_appointment(db: Session, payload):
    _ensure_patient(db, payload.clinic_id, payload.patient_id)
    conflict = db.scalars(
        select(Appointment).where(
            Appointment.clinic_id == payload.clinic_id,
            Appointment.doctor_id == payload.doctor_id,
            Appointment.appointment_at == payload.appointment_at,
            Appointment.status != "cancelled",
        )
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="Doctor already booked for that slot")

    appt = Appointment(
        clinic_id=payload.clinic_id,
        patient_id=payload.patient_id,
        doctor_id=payload.doctor_id,
        reason=payload.reason,
        appointment_at=payload.appointment_at,
        priority=payload.priority,
        notes=payload.notes,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt

def list_appointments(db: Session, clinic_id: int):
    rows = db.scalars(select(Appointment).where(Appointment.clinic_id == clinic_id).order_by(Appointment.appointment_at.asc())).all()
    return rows

def update_appointment(db: Session, appointment_id: int, payload):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for field in ("appointment_at", "doctor_id", "reason", "status", "priority", "notes"):
        value = getattr(payload, field, None)
        if value is not None:
            setattr(appt, field, value)
    db.commit()
    db.refresh(appt)
    return appt

def cancel_appointment(db: Session, appointment_id: int):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = "cancelled"
    db.commit()
    db.refresh(appt)
    return appt
