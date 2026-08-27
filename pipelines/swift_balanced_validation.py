"""
SWIFT Path 1 - Balanced Logistic Regression Validation Script
=============================================================
Reruns Path 1 hyperparameter optimization and evaluation using class_weight='balanced'.

Methodology:
  1. 5-fold stratified CV Optuna tuning on X_train ONLY (scoring='roc_auc').
  2. Fixed class_weight='balanced' for screening priority.
  3. Single evaluation on untouched test set (X_test, y_test).
  4. 1,000 bootstrap replications for 95% percentile CIs.

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
    confusion_matrix, f1_score, matthews_corrcoef, precision_score,
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


def calculate_metrics(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    
    return {
        "roc_auc":           roc_auc_score(y_true, y_prob),
        "auprc":             average_precision_score(y_true, y_prob),
        "accuracy":          accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "precision":         precision_score(y_true, y_pred, zero_division=0),
        "recall":            recall_score(y_true, y_pred, zero_division=0),
        "specificity":       specificity,
        "f1":                f1_score(y_true, y_pred, zero_division=0),
        "mcc":               matthews_corrcoef(y_true, y_pred),
        "brier_score":       brier_score_loss(y_true, y_prob),
    }


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
# Optuna: 60 trials, 5-fold CV on X_train ONLY with class_weight='balanced'
# ═══════════════════════════════════════════════════════════════
print("\n[Optuna Path 1] Tuning Logistic Regression with class_weight='balanced'...")

def objective(trial):
    C        = trial.suggest_float("C", 0.001, 10.0, log=True)
    solver   = trial.suggest_categorical("solver", ["liblinear", "lbfgs"])
    max_iter = trial.suggest_int("max_iter", 500, 5000)

    clf = LogisticRegression(
        C=C, solver=solver, max_iter=max_iter,
        class_weight="balanced", random_state=42
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
best_params["class_weight"] = "balanced"

print(f"  Best CV ROC-AUC (train-only, balanced): {best_cv_auc:.4f}")
print(f"  Best params: {best_params}")

# Fit final model on full X_train, evaluate ONCE on X_test
tuned_clf = LogisticRegression(
    C=best_params["C"],
    solver=best_params["solver"],
    max_iter=best_params["max_iter"],
    class_weight="balanced",
    random_state=42,
)
tuned_pipe = Pipeline([
    ("pre", build_preprocessor(X_train)),
    ("clf", tuned_clf),
])
tuned_pipe.fit(X_train, y_train)

proba_tuned = tuned_pipe.predict_proba(X_test)[:, 1]
test_results = calculate_metrics(y_test, proba_tuned, threshold=0.5)

print(f"\n  Test-set results (balanced, first evaluation):")
for k, v in test_results.items():
    print(f"    {k:<24}: {v:.4f}")

optuna_out = {
    "best_cv_roc_auc_trainonly": best_cv_auc,
    **{f"best_{k}": v for k, v in best_params.items()},
    **{f"test_{k}": v for k, v in test_results.items()},
    "note": (
        "Optuna (n=60 trials) with class_weight='balanced' used 5-fold stratified CV on X_train only. "
        "Test set evaluated exactly once after final model selection. No test leakage."
    ),
}
pd.DataFrame([optuna_out]).to_csv(
    OUT_DIR / "balanced_optuna_corrected_results.csv", index=False
)
study.trials_dataframe().to_csv(
    OUT_DIR / "balanced_optuna_all_trials.csv", index=False
)
print(f"\n  Saved: balanced_optuna_corrected_results.csv")


# ═══════════════════════════════════════════════════════════════
# Bootstrap 95% CIs (n=1000)
# ═══════════════════════════════════════════════════════════════
print("\n[Bootstrap 95% CIs] Running 1,000 replications...")

N_BOOTSTRAPS = 1000
rng = np.random.RandomState(42)
boot_records = []

for _ in range(N_BOOTSTRAPS):
    idx  = rng.choice(len(X_test), size=len(X_test), replace=True)
    y_b  = y_test.iloc[idx].values
    p_b  = proba_tuned[idx]
    if len(np.unique(y_b)) < 2:
        continue
    boot_records.append(calculate_metrics(y_b, p_b, threshold=0.5))

boot_df = pd.DataFrame(boot_records)
boot_df.to_csv(OUT_DIR / "balanced_bootstrap_1000_raw.csv", index=False)

ci_rows = []
for metric in boot_df.columns:
    vals = boot_df[metric].dropna()
    point_est = test_results[metric]
    ci_lower = float(np.percentile(vals, 2.5))
    ci_upper = float(np.percentile(vals, 97.5))
    ci_rows.append({
        "metric":            metric,
        "test_point_est":    round(float(point_est), 4),
        "boot_mean":         round(float(vals.mean()), 4),
        "ci_lower_2.5pct":  round(ci_lower, 4),
        "ci_upper_97.5pct": round(ci_upper, 4),
        "std":               round(float(vals.std()), 4),
        "n_valid":           int(len(vals)),
    })

ci_df = pd.DataFrame(ci_rows)
ci_df.to_csv(OUT_DIR / "balanced_bootstrap_95CI.csv", index=False)

print(f"\n  {'Metric':<20} {'Test Point':>10}  {'Boot Mean':>10}  {'CI 2.5%':>10}  {'CI 97.5%':>10}")
print(f"  {'-'*66}")
for _, row in ci_df.iterrows():
    print(
        f"  {row['metric']:<20} {row['test_point_est']:>10.4f}  {row['boot_mean']:>10.4f}"
        f"  {row['ci_lower_2.5pct']:>10.4f}  {row['ci_upper_97.5pct']:>10.4f}"
    )

print(f"\n  Valid replications: {len(boot_records)} / {N_BOOTSTRAPS}")
print(f"  Saved: balanced_bootstrap_95CI.csv")
print(f"\n[DONE] Path 1 Complete. All balanced results in:\n  {OUT_DIR}")
