"""Train and evaluate the SWIFT Logistic Regression model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import optuna
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             brier_score_loss, f1_score, precision_score, recall_score,
                             roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

from feature_engineering import build_preprocessor, prepare_xy

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "database_majorproj.csv"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)


def metrics(y_true, probabilities, threshold=0.5):
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = pd.crosstab(y_true, predictions, rownames=["actual"], colnames=["predicted"], dropna=False).reindex(index=[0, 1], columns=[0, 1], fill_value=0).to_numpy().ravel()
    return {
        "roc_auc": roc_auc_score(y_true, probabilities),
        "auprc": average_precision_score(y_true, probabilities),
        "accuracy": accuracy_score(y_true, predictions),
        "balanced_accuracy": balanced_accuracy_score(y_true, predictions),
        "precision": precision_score(y_true, predictions, zero_division=0),
        "recall": recall_score(y_true, predictions, zero_division=0),
        "specificity": tn / (tn + fp),
        "f1": f1_score(y_true, predictions, zero_division=0),
        "brier_score": brier_score_loss(y_true, probabilities),
    }


def main():
    features, target = prepare_xy(pd.read_csv(DATA_PATH))
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.25, stratify=target, random_state=42)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    def objective(trial):
        model = Pipeline([
            ("preprocess", build_preprocessor(x_train)),
            ("model", LogisticRegression(
                C=trial.suggest_float("C", 0.001, 10.0, log=True),
                solver=trial.suggest_categorical("solver", ["liblinear", "lbfgs"]),
                max_iter=trial.suggest_int("max_iter", 500, 5000),
                class_weight="balanced",
                random_state=42,
            )),
        ])
        return cross_val_score(model, x_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1).mean()

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=60, show_progress_bar=False)
    params = study.best_trial.params
    model = Pipeline([
        ("preprocess", build_preprocessor(x_train)),
        ("model", LogisticRegression(**params, class_weight="balanced", random_state=42)),
    ])
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]
    final_metrics = metrics(y_test, probabilities)

    joblib.dump(model, ARTIFACTS / "swift_model.joblib")
    metadata = {
        "model": "Balanced Logistic Regression",
        "train_rows": len(x_train), "test_rows": len(x_test),
        "best_cv_roc_auc": study.best_value, "best_parameters": params,
        "test_metrics": final_metrics,
        "decision_threshold": 0.5,
        "feature_columns": features.columns.tolist(),
    }
    (ARTIFACTS / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
