from fastapi import APIRouter, Depends
from app.quantum.qaoa import QUANTUM_BACKEND, optimise_schedule
from app.core.dependencies import require_doctor

router = APIRouter()

@router.get("/status")
def status(_: dict = Depends(require_doctor)):
    return {"backend": QUANTUM_BACKEND}

@router.post("/schedule")
def schedule(payload: dict, _: dict = Depends(require_doctor)):
    patients = payload.get("patients", [])
    return optimise_schedule(patients)
