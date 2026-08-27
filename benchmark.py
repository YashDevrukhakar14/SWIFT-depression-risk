"""Compare Random Forest and XGBoost on the same SWIFT split."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from feature_engineering import build_preprocessor, prepare_xy

ROOT = Path(__file__).resolve().parent


def main():
    features, target = prepare_xy(pd.read_csv(ROOT / "database_majorproj.csv"))
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.25, stratify=target, random_state=42
    )
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            eval_metric="logloss", random_state=42, n_jobs=-1
        ),
    }
    rows = []
    for name, estimator in models.items():
        pipeline = Pipeline([
            ("preprocess", build_preprocessor(x_train)),
            ("model", estimator),
        ])
        pipeline.fit(x_train, y_train)
        probability = pipeline.predict_proba(x_test)[:, 1]
        rows.append({
            "model": name,
            "roc_auc": roc_auc_score(y_test, probability),
            "auprc": average_precision_score(y_test, probability),
        })
    result = pd.DataFrame(rows)
    result.to_csv(ROOT / "artifacts" / "tree_model_comparison.csv", index=False)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
