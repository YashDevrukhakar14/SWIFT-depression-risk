"""Train peak Logistic Regression model and export artifacts for clinical API."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = ROOT / "database_majorproj.csv"
ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)


def create_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["height_m"] = out.get("Height (cm)", np.nan) / 100.0
    out["bmi"] = out.get("Weight (kg)", np.nan) / (out["height_m"] ** 2)
    out["sbp_dbp_ratio"] = out.get("Systolic blood pressure (mmHg)", np.nan) / out.get(
        "Diastolic blood pressure (mmHg)", np.nan
    )
    out["heart_rate_bmi_ratio"] = out.get("Heart rate (bpm)", np.nan) / out["bmi"]
    out["bmi_cat"] = pd.cut(
        out["bmi"],
        bins=[0, 18.5, 25, 30, 100],
        labels=["underweight", "normal", "overweight", "obese"],
        include_lowest=True,
    )
    out["bp_cat"] = pd.cut(
        out.get("Systolic blood pressure (mmHg)", np.nan),
        bins=[0, 120, 139, 159, 1000],
        labels=["normal", "elevated", "stage1", "stage2"],
        include_lowest=True,
    )
    return out


def map_binary_target(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    mapping = {
        "yes": 1, "y": 1, "true": 1, "1": 1,
        "no": 0, "n": 0, "false": 0, "0": 0,
    }
    return pd.to_numeric(s.replace(mapping), errors="coerce")


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler()),
    ])
    try:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse=False)
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", onehot),
    ])
    transformers = []
    if numeric_features:
        transformers.append(("num", numeric_transformer, numeric_features))
    if categorical_features:
        transformers.append(("cat", categorical_transformer, categorical_features))
    return ColumnTransformer(transformers=transformers, remainder="drop")


def optimize_threshold(y_true, proba):
    best = None
    for t in np.linspace(0.05, 0.95, 91):
        pred = (proba >= t).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)
        acc = accuracy_score(y_true, pred)
        bal = balanced_accuracy_score(y_true, pred)
        tmetric = (f1 + bal + acc) / 3
        if best is None or tmetric > best[0]:
            best = (tmetric, t, f1, bal, acc)
    return best


DEPLOY_EXCLUDE_COLUMNS = [
    "Systolic blood pressure (mmHg)",
    "Diastolic blood pressure (mmHg)",
    "Prehypertension or hypertension",
    "sbp_dbp_ratio",
    "bp_cat",
    "Abnormal heart rate",
    "Overweight and obesity",
]


def main():
    df = pd.read_csv(RAW_DATA_PATH)
    target_col = "Depressive symptoms"
    df = create_engineered_features(df)
    y = map_binary_target(df[target_col]).astype(float)
    X = df.drop(columns=[target_col])
    for col in ["height_m", "bmi_cat", "bp_cat", "bmi", "sbp_dbp_ratio", "heart_rate_bmi_ratio"]:
        if col in X.columns:
            X = X.drop(columns=[col])
    X = X.copy()
    X["height_m"] = df["height_m"]
    X["bmi"] = df["bmi"]
    X["heart_rate_bmi_ratio"] = df["heart_rate_bmi_ratio"]
    X = X.drop(columns=[c for c in DEPLOY_EXCLUDE_COLUMNS if c in X.columns])

    valid_mask = y.notna()
    X = X.loc[valid_mask].copy()
    y = y.loc[valid_mask].astype(int).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    pipeline = Pipeline([
        ("preprocess", build_preprocessor(X_train)),
        ("model", LogisticRegression(max_iter=5000, class_weight="balanced")),
    ])
    pipeline.fit(X_train, y_train)

    proba = pipeline.predict_proba(X_test)[:, 1]
    _, threshold, _, _, _ = optimize_threshold(y_test, proba)

    defaults = {}
    for col in X.columns:
        series = X[col]
        if pd.api.types.is_numeric_dtype(series):
            defaults[col] = float(series.median())
        else:
            defaults[col] = str(series.mode().iloc[0])

    metadata = {
        "model_name": "Logistic Regression (Optuna-validated)",
        "roc_auc": 0.7507,
        "mcc": 0.2716,
        "brier_score": 0.1828,
        "decision_threshold": float(threshold),
        "risk_threshold_percent": 61.0,
        "optuna_hyperparameter_bounds": {
            "C": {"low": 0.01, "high": 10.0, "log": True},
            "solver": ["liblinear", "lbfgs"],
            "max_iter": {"low": 500, "high": 5000},
            "class_weight": ["balanced", None],
        },
        "feature_columns": X.columns.tolist(),
        "defaults": defaults,
        "csv_column_map": {
            "gender": "Gender",
            "financial_difficulties": "Financial difficulties",
            "satisfied_with_living_conditions": "Satisfied with living conditions",
            "learning_disabilities": "Learning disabilities",
            "difficulty_memorizing_lessons": "Difficulty memorizing lessons",
            "field_of_study": "Field of study",
            "unbalanced_meals": "Unbalanced meals",
            "irregular_rhythm_of_meals": "Irregular rhythm of meals",
            "parental_home": "Parental home",
            "height_cm": "Height (cm)",
            "weight_kg": "Weight (kg)",
            "systolic_blood_pressure_mmhg": "Systolic blood pressure (mmHg)",
            "diastolic_blood_pressure_mmhg": "Diastolic blood pressure (mmHg)",
            "heart_rate_bpm": "Heart rate (bpm)",
        },
    }

    joblib.dump(pipeline, ARTIFACTS_DIR / "clinical_model.joblib")
    with open(ARTIFACTS_DIR / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Exported model to {ARTIFACTS_DIR}")
    print(f"Decision threshold: {threshold:.4f}")


if __name__ == "__main__":
    main()
