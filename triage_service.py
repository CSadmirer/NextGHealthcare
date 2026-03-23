from app.models.triage import TriageResult
from sqlalchemy.orm import Session

def triage_score(symptoms: dict, vitals: dict) -> tuple[int, str, str]:
    score = 0
    text = "Routine"

    bp_sys = int(vitals.get("bp_sys", 120))
    bp_dia = int(vitals.get("bp_dia", 80))
    pulse = int(vitals.get("pulse", 72))
    temp = float(vitals.get("temp", 37.0))
    spo2 = int(vitals.get("spo2", 98))
    rr = int(vitals.get("rr", 16))
    complaint = " ".join([str(k) for k, v in symptoms.items() if v]).lower()

    if "chest pain" in complaint or "shortness of breath" in complaint or "dyspnea" in complaint:
        score += 30
    if bp_sys >= 180 or bp_dia >= 120:
        score += 30
    elif bp_sys >= 140:
        score += 15
    if spo2 < 90:
        score += 30
    elif spo2 < 94:
        score += 15
    if pulse > 130 or pulse < 40:
        score += 20
    elif pulse > 100:
        score += 8
    if temp >= 39.5:
        score += 15
    elif temp >= 38.5:
        score += 8
    if rr > 25 or rr < 10:
        score += 15
    elif rr > 20:
        score += 6

    score = min(score, 100)
    if score >= 75:
        text = "Emergency"
    elif score >= 45:
        text = "Urgent"
    else:
        text = "Routine"

    summary = f"Triage score {score}/100. Priority: {text}."
    return score, text, summary

def save_triage(db: Session, clinic_id: int, patient_id: int | None, symptoms: dict, vitals: dict):
    score, band, summary = triage_score(symptoms, vitals)
    row = TriageResult(
        clinic_id=clinic_id,
        patient_id=patient_id,
        symptoms=symptoms,
        vitals=vitals,
        score=score,
        band=band,
        summary=summary,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
