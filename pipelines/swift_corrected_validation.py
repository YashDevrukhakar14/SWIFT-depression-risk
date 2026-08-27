"""
SWIFT Corrected Validation Script
==================================
Fixes two audit findings from Step 1:

  FIX 1 — Optuna now tunes using 5-fold CV on X_train ONLY.
           The test set is never seen during hyperparameter search.

  FIX 2 — Bootstrap CIs computed with n=1000 replications.
           Percentile 95% CI reported for all primary metrics.

Run:
    python swift_corrected_validation.py

Outputs saved to: publication_results/corrected/
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, brier_score_loss,
    f1_score, matthews_corrcoef, precision_score,
    recall_score, roc_auc_score, average_precision_score,
)
from sklearn.model_selection import (
    cross_val_score, StratifiedKFold, train_test_split
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import optuna

optuna.logging.set_verbosity(optuna.logging.WARNING)
warnings.filterwarnings("ignore")

RAW_DATA_PATH = Path(__file__).resolve().parent / "database_majorproj.csv"
OUT_DIR = Path(__file__).resolve().parent / "publication_results" / "corrected"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def map_binary_target(series):
    s = series.astype(str).str.strip().str.lower()
    mapping = {"yes": 1, "y": 1, "true": 1, "1": 1,
               "no": 0, "n": 0, "false": 0, "0": 0}
    s = s.replace(mapping)
    return pd.to_numeric(s, errors="coerce").astype("Int64")


def create_engineered_features(df):
    out = df.copy()
    out["height_m"] = out["Height (cm)"] / 100.0
    out["bmi"] = out["Weight (kg)"] / (out["height_m"] ** 2)
    out["sbp_dbp_ratio"] = (
        out["Systolic blood pressure (mmHg)"] /
        out["Diastolic blood pressure (mmHg)"]
    )
    out["heart_rate_bmi_ratio"] = out["Heart rate (bpm)"] / out["bmi"]
    return out


def build_preprocessor(X):
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(exclude=[np.number]).columns.tolist()
    num_pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc",  StandardScaler()),
    ])
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
    cat_pipe = Pipeline([
        ("imp", SimpleImputer(strategy="most_frequent")),
        ("ohe", ohe),
    ])
    transformers = []
    if num_cols:
        transformers.append(("num", num_pipe, num_cols))
    if cat_cols:
        transformers.append(("cat", cat_pipe, cat_cols))
    return ColumnTransformer(transformers, remainder="drop")


# ── Load & split ─────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv(RAW_DATA_PATH)
print(f"  Shape: {df.shape}")

df = create_engineered_features(df)
y = map_binary_target(df["Depressive symptoms"]).astype(float)
X = df.drop(columns=["Depressive symptoms"])
for col in ["height_m", "bmi", "sbp_dbp_ratio", "heart_rate_bmi_ratio"]:
    X[col] = df[col]

valid_mask = y.notna()
X = X.loc[valid_mask].copy()
y = y.loc[valid_mask].astype(int).copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)
X_train = X_train.reset_index(drop=True)
X_test  = X_test.reset_index(drop=True)
y_train = y_train.reset_index(drop=True)
y_test  = y_test.reset_index(drop=True)

print(f"  Train: {len(X_train)} | Test: {len(X_test)}")
print(f"  Positive rate (test): {y_test.mean():.3f}")


# ═══════════════════════════════════════════════════════════════
# FIX 1 — Optuna: 5-fold CV on X_train ONLY
# ═══════════════════════════════════════════════════════════════
print("\n[FIX 1] Optuna — 60 trials, 5-fold CV on X_train only...")

def objective(trial):
    C        = trial.suggest_float("C",        0.001, 10.0, log=True)
    solver   = trial.suggest_categorical("solver", ["liblinear", "lbfgs"])
    max_iter = trial.suggest_int("max_iter", 500, 5000)
    cw       = trial.suggest_categorical("class_weight", ["balanced", None])

    clf = LogisticRegression(
        C=C, solver=solver, max_iter=max_iter,
        class_weight=cw, random_state=42
    )
    pipe = Pipeline([
        ("pre", build_preprocessor(X_train)),
        ("clf", clf),
    ])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipe, X_train, y_train,
                             cv=cv, scoring="roc_auc", n_jobs=-1)
    return scores.mean()


study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=42)
)
study.optimize(objective, n_trials=60, show_progress_bar=False)

best_params  = study.best_trial.params
best_cv_auc  = study.best_value
print(f"  Best CV ROC-AUC (train-only): {best_cv_auc:.4f}")
print(f"  Best params: {best_params}")

# Fit final model on full X_train, evaluate ONCE on X_test
tuned_clf = LogisticRegression(
    C=best_params["C"],
    solver=best_params["solver"],
    max_iter=best_params["max_iter"],
    class_weight=best_params["class_weight"],
    random_state=42,
)
tuned_pipe = Pipeline([
    ("pre", build_preprocessor(X_train)),
    ("clf", tuned_clf),
])
tuned_pipe.fit(X_train, y_train)

proba_tuned = tuned_pipe.predict_proba(X_test)[:, 1]
pred_tuned  = (proba_tuned >= 0.5).astype(int)

results = {
    "roc_auc":           roc_auc_score(y_test, proba_tuned),
    "auprc":             average_precision_score(y_test, proba_tuned),
    "f1":                f1_score(y_test, pred_tuned, zero_division=0),
    "recall":            recall_score(y_test, pred_tuned, zero_division=0),
    "precision":         precision_score(y_test, pred_tuned, zero_division=0),
    "accuracy":          accuracy_score(y_test, pred_tuned),
    "balanced_accuracy": balanced_accuracy_score(y_test, pred_tuned),
    "mcc":               matthews_corrcoef(y_test, pred_tuned),
    "brier_score":       brier_score_loss(y_test, proba_tuned),
}

print(f"\n  Test-set results (first evaluation, no leakage):")
for k, v in results.items():
    print(f"    {k:<24}: {v:.4f}")

optuna_out = {
    "best_cv_roc_auc_trainonly": best_cv_auc,
    **{f"best_{k}": v for k, v in best_params.items()},
    **{f"test_{k}": v for k, v in results.items()},
    "note": (
        "Optuna (n=60 trials) used 5-fold stratified CV on X_train only. "
        "Test set evaluated exactly once after final model selection. "
        "No test leakage."
    ),
}
pd.DataFrame([optuna_out]).to_csv(
    OUT_DIR / "optuna_corrected_results.csv", index=False
)
study.trials_dataframe().to_csv(
    OUT_DIR / "optuna_all_trials.csv", index=False
)
print(f"\n  Saved: optuna_corrected_results.csv")


# ═══════════════════════════════════════════════════════════════
# FIX 2 — Bootstrap 95% CIs (n=1000)
# ═══════════════════════════════════════════════════════════════
print("\n[FIX 2] Bootstrap 95% CIs — 1,000 replications...")

N_BOOTSTRAPS = 1000
rng = np.random.RandomState(42)
boot_records = []

for _ in range(N_BOOTSTRAPS):
    idx  = rng.choice(len(X_test), size=len(X_test), replace=True)
    y_b  = y_test.iloc[idx].values
    p_b  = proba_tuned[idx]
    if len(np.unique(y_b)) < 2:
        continue
    pred_b = (p_b >= 0.5).astype(int)
    boot_records.append({
        "roc_auc":           roc_auc_score(y_b, p_b),
        "auprc":             average_precision_score(y_b, p_b),
        "f1":                f1_score(y_b, pred_b, zero_division=0),
        "recall":            recall_score(y_b, pred_b, zero_division=0),
        "precision":         precision_score(y_b, pred_b, zero_division=0),
        "accuracy":          accuracy_score(y_b, pred_b),
        "balanced_accuracy": balanced_accuracy_score(y_b, pred_b),
        "mcc":               matthews_corrcoef(y_b, pred_b),
        "brier_score":       brier_score_loss(y_b, p_b),
    })

boot_df = pd.DataFrame(boot_records)
boot_df.to_csv(OUT_DIR / "bootstrap_1000_raw.csv", index=False)

ci_rows = []
for metric in boot_df.columns:
    vals = boot_df[metric].dropna()
    ci_rows.append({
        "metric":            metric,
        "point_estimate":    round(float(vals.mean()), 4),
        "ci_lower_2.5pct":  round(float(np.percentile(vals, 2.5)), 4),
        "ci_upper_97.5pct": round(float(np.percentile(vals, 97.5)), 4),
        "std":               round(float(vals.std()), 4),
        "n_valid":           int(len(vals)),
    })

ci_df = pd.DataFrame(ci_rows)
ci_df.to_csv(OUT_DIR / "bootstrap_95CI.csv", index=False)

print(f"\n  {'Metric':<22} {'Point':>8}  {'CI 2.5%':>10}  {'CI 97.5%':>10}")
print(f"  {'-'*56}")
for _, row in ci_df.iterrows():
    print(
        f"  {row['metric']:<22} {row['point_estimate']:>8.4f}"
        f"  {row['ci_lower_2.5pct']:>10.4f}  {row['ci_upper_97.5pct']:>10.4f}"
    )

print(f"\n  Valid replications: {len(boot_records)} / {N_BOOTSTRAPS}")
print(f"  Saved: bootstrap_95CI.csv")
print(f"\n✓ Done. All corrected results in:\n  {OUT_DIR}")
