from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.triage_service import triage_score
from app.services.ai_service import predict_clinical_risks
from app.quantum.qaoa import optimise_schedule

@dataclass
class StepResult:
    name: str
    status: str
    note: str = ""
    data: dict = field(default_factory=dict)

def run_pipeline(patient_name: str, age: int, symptoms: dict, vitals: dict, other_patients: list[dict], n_chronic: int = 0, on_anticoag: bool = False, severe_allergy: bool = False) -> dict[str, Any]:
    score, band, summary = triage_score(symptoms, vitals)
    risk_input = {
        "age": age,
        "sex": 1,
        "cp": 0,
        "trestbps": vitals.get("bp_sys", 120),
        "chol": 220,
        "fbs": 0,
        "restecg": 0,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 0.5,
        "slope": 1,
        "ca": 0,
        "thal": 1,
        "pregnancies": 0,
        "glucose": 120,
        "bp": vitals.get("bp_sys", 120),
        "skin": 20,
        "insulin": 100,
        "bmi": 28.0,
        "pedigree": 0.5,
    }
    ai = predict_clinical_risks(risk_input)
    schedule = optimise_schedule([{"name": patient_name, "priority": 3 if band == "Emergency" else 2 if band == "Urgent" else 1}] + (other_patients or []))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "patient_name": patient_name,
        "triage": {"score": score, "band": band, "summary": summary},
        "ai": ai,
        "schedule": schedule,
        "disclaimer": ai["disclaimer"],
    }
