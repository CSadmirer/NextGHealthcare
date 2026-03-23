from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.triage import TriageIn
from app.services.triage_service import save_triage
from app.core.dependencies import require_staff

router = APIRouter()

@router.post("/assess")
def assess(payload: TriageIn, db: Session = Depends(get_db), _: dict = Depends(require_staff)):
    row = save_triage(db, payload.clinic_id, payload.patient_id, payload.symptoms, payload.vitals)
    return {"score": row.score, "band": row.band, "summary": row.summary, "id": row.id}
