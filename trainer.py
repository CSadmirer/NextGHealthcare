from pathlib import Path
import json
import logging
from datetime import datetime
import numpy as np
import pandas as pd
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

log = logging.getLogger(__name__)
BASE = Path(__file__).resolve().parent / "saved"

HEART_FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
DIAB_FEATURES = ["pregnancies", "glucose", "bp", "skin", "insulin", "bmi", "pedigree", "age"]

def _download_heart():
    try:
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
        cols = HEART_FEATURES + ["target"]
        df = pd.read_csv(url, names=cols, na_values="?")
        df = df.dropna()
        df["target"] = (pd.to_numeric(df["target"], errors="coerce") > 0).astype(int)
        return df[HEART_FEATURES], df["target"]
    except Exception as exc:
        log.warning("Falling back to synthetic heart dataset: %s", exc)
        return _synthetic_heart()

def _download_diabetes():
    try:
        url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
        df = pd.read_csv(url, header=None)
        df.columns = DIAB_FEATURES + ["target"]
        return df[DIAB_FEATURES], df["target"].astype(int)
    except Exception as exc:
        log.warning("Falling back to synthetic diabetes dataset: %s", exc)
        return _synthetic_diabetes()

def _synthetic_heart(n=800):
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "age": rng.integers(29, 80, n),
        "sex": rng.integers(0, 2, n),
        "cp": rng.integers(0, 4, n),
        "trestbps": rng.integers(90, 200, n),
        "chol": rng.integers(120, 500, n),
        "fbs": rng.integers(0, 2, n),
        "restecg": rng.integers(0, 2, n),
        "thalach": rng.integers(70, 210, n),
        "exang": rng.integers(0, 2, n),
        "oldpeak": rng.random(n) * 6,
        "slope": rng.integers(0, 3, n),
        "ca": rng.integers(0, 4, n),
        "thal": rng.integers(0, 3, n),
    })
    score = (df["age"] > 55).astype(int) + (df["chol"] > 240).astype(int) + (df["trestbps"] > 140).astype(int) + (df["exang"] > 0).astype(int)
    y = (score >= 2).astype(int)
    return df, y

def _synthetic_diabetes(n=1000):
    rng = np.random.default_rng(7)
    df = pd.DataFrame({
        "pregnancies": rng.integers(0, 15, n),
        "glucose": rng.integers(50, 220, n),
        "bp": rng.integers(40, 140, n),
        "skin": rng.integers(0, 99, n),
        "insulin": rng.integers(0, 846, n),
        "bmi": rng.random(n) * 50,
        "pedigree": rng.random(n) * 2.5,
        "age": rng.integers(18, 80, n),
    })
    score = (df["glucose"] > 125).astype(int) + (df["bmi"] > 30).astype(int) + (df["age"] > 45).astype(int)
    y = (score >= 2).astype(int)
    return df, y

def _train_binary(df: pd.DataFrame, y: pd.Series, features: list[str], name: str):
    x_train, x_test, y_train, y_test = train_test_split(df[features], y, test_size=0.2, random_state=42, stratify=y)
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000)),
    ])
    pipe.fit(x_train, y_train)
    preds = pipe.predict(x_test)
    f1 = f1_score(y_test, preds)
    BASE.mkdir(parents=True, exist_ok=True)
    out_dir = BASE / name
    out_dir.mkdir(parents=True, exist_ok=True)
    version = "v1"
    model_path = out_dir / f"{version}_model.pkl"
    joblib.dump(pipe, model_path)
    (out_dir / f"{version}_features.json").write_text(json.dumps(features))
    (out_dir / f"{version}_meta.json").write_text(json.dumps({
        "trained_at": datetime.utcnow().isoformat(),
        "f1_score": float(f1),
        "algorithm": "logistic_regression",
        "name": name,
    }, indent=2))
    return f1, classification_report(y_test, preds, zero_division=0)

def train_all():
    heart_df, heart_y = _download_heart()
    diab_df, diab_y = _download_diabetes()
    heart_score, heart_report = _train_binary(heart_df, heart_y, HEART_FEATURES, "heart_disease")
    diab_score, diab_report = _train_binary(diab_df, diab_y, DIAB_FEATURES, "diabetes")
    print({"heart_f1": heart_score, "diabetes_f1": diab_score})
    print("Heart report:\n", heart_report)
    print("Diabetes report:\n", diab_report)

if __name__ == "__main__":
    train_all()
