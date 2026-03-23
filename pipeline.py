from fastapi import APIRouter, Depends
from app.schemas.pipeline import PipelineRequest
from app.services.pipeline_service import run_pipeline
from app.core.dependencies import require_doctor

router = APIRouter()

@router.post("/run")
def run(payload: PipelineRequest, _: dict = Depends(require_doctor)):
    return run_pipeline(
        payload.patient_name,
        payload.age,
        payload.symptoms,
        payload.vitals,
        payload.other_patients,
        payload.n_chronic,
        payload.on_anticoag,
        payload.severe_allergy,
    )
