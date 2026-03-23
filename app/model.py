from pathlib import Path
import json
import joblib
import numpy as np

MODEL_DIR = Path(__file__).resolve().parent / "saved"

def _latest_model_path(name: str) -> Path | None:
    d = MODEL_DIR / name
    if not d.exists():
        return None
    models = sorted(d.glob("*_model.pkl"))
    return models[-1] if models else None

def load_model_bundle(name: str = "heart_disease") -> dict | None:
    path = _latest_model_path(name)
    if not path:
        return None
    meta = path.with_name(path.name.replace("_model.pkl", "_meta.json"))
    features = path.with_name(path.name.replace("_model.pkl", "_features.json"))
    bundle = {"model": joblib.load(path)}
    if meta.exists():
        bundle["meta"] = json.loads(meta.read_text())
    if features.exists():
        bundle["features"] = json.loads(features.read_text())
    return bundle

def predict_from_bundle(bundle: dict, values: dict) -> dict:
    model = bundle["model"]
    features = bundle.get("features", [])
    x = np.array([[float(values.get(f, 0)) for f in features]])
    prob = None
    pred = model.predict(x)[0]
    if hasattr(model, "predict_proba"):
        prob = float(model.predict_proba(x).max())
    else:
        prob = 0.5
    return {"label": str(pred), "confidence": round(prob, 4)}

def predict_risks(values: dict) -> dict:
    out = {}
    for name in ("heart_disease", "diabetes"):
        bundle = load_model_bundle(name)
        if bundle:
            out[name] = predict_from_bundle(bundle, values)
    return out
