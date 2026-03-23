from app.ai.model import predict_risks
from app.ai.model import load_model_bundle
from app.ai.explainer import explain_prediction

DISCLAIMER = "This is an AI-assisted suggestion, not a final diagnosis."

def predict_clinical_risks(values: dict) -> dict:
    bundles = {name: load_model_bundle(name) for name in ("heart_disease", "diabetes")}
    risks = predict_risks(values)
    explanations = {
        name: explain_prediction(bundle)
        for name, bundle in bundles.items()
        if bundle
    }
    top3 = []
    for name, r in risks.items():
        top3.append({
            "condition": name.replace("_", " ").title(),
            "label": r.get("label"),
            "confidence": r.get("confidence", 0.0),
        })
    top3 = sorted(top3, key=lambda x: x["confidence"], reverse=True)[:3]
    return {
        "predictions": risks,
        "top3": top3,
        "explanations": explanations,
        "disclaimer": DISCLAIMER,
    }
