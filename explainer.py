def explain_prediction(model_bundle: dict | None) -> list[dict]:
    if not model_bundle:
        return [{"feature": "clinical_rules", "importance": 1.0, "reason": "No trained model found; using rule-based safety layer."}]
    model = model_bundle["model"]
    features = model_bundle.get("features", [])
    if hasattr(model, "feature_importances_"):
        imp = list(model.feature_importances_)
    elif hasattr(model, "coef_"):
        arr = model.coef_[0]
        imp = [abs(float(v)) for v in arr]
    else:
        imp = [1.0 / max(len(features), 1)] * max(len(features), 1)
    pairs = sorted(zip(features, imp), key=lambda x: x[1], reverse=True)
    return [{"feature": f, "importance": float(round(v, 4))} for f, v in pairs[:5]]
