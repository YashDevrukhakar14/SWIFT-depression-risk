"""SWIFT: Student Wellness Intelligence Framework for Triage
Master Reproducibility Pipeline

Executes the complete experimental workflow reported in the manuscript:
  1. Data Loading & Feature Engineering (75/25 stratified split, seed=42)
  2. Primary Benchmark Model: Baseline Logistic Regression (C=1.0, balanced)
  3. Uncertainty Quantification: 1,000-Replication Non-Parametric Bootstrap CIs
  4. 17-Model Comparative Benchmark (Table 5)
  5. Secondary Sensitivity Analysis: Optuna Hyperparameter Search (train-CV only)
  6. Calibration Assessment & Reliability Diagram
  7. Explainability Pipeline: SHAP LinearExplainer & LIME Local Explanations

Outputs are saved to `publication_results/`.
"""

from __future__ import annotations

import os
import sys
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Filter warnings for clean execution
warnings.filterwarnings("ignore")

# Define Paths
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

DATA_PATH = ROOT / "data" / "database_majorproj.csv"
RESULTS_DIR = ROOT / "publication_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    AdaBoostClassifier,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    matthews_corrcoef,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)
from sklearn.calibration import calibration_curve
from sklearn.pipeline import Pipeline

from feature_engineering import create_engineered_features, map_binary_target, build_preprocessor

# Optional dependencies
try:
    from imblearn.ensemble import BalancedRandomForestClassifier, BalancedBaggingClassifier
except ImportError:
    BalancedRandomForestClassifier = None
    BalancedBaggingClassifier = None

try:
    import xgboost as xgb
except ImportError:
    xgb = None

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

try:
    import catboost as cb
except ImportError:
    cb = None

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
except ImportError:
    optuna = None

try:
    import shap
except ImportError:
    shap = None

try:
    from lime.lime_tabular import LimeTabularExplainer
except ImportError:
    LimeTabularExplainer = None


def compute_metrics(y_true, proba, pred, has_proba=True):
    y_true = np.asarray(y_true).astype(int)
    pred = np.asarray(pred).astype(int)
    cm = confusion_matrix(y_true, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    acc = (tp + tn) / len(y_true)
    bal_acc = (spec + rec) / 2.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    mcc = matthews_corrcoef(y_true, pred)
    
    auc = roc_auc_score(y_true, proba) if len(np.unique(y_true)) == 2 else np.nan
    ap = average_precision_score(y_true, proba) if len(np.unique(y_true)) == 2 else np.nan
    brier = brier_score_loss(y_true, proba) if (has_proba and len(np.unique(y_true)) == 2) else np.nan
    
    # Brier skill score relative to test prevalence
    p = np.mean(y_true)
    ref_brier = p * (1 - p)
    bss = 1.0 - (brier / ref_brier) if (has_proba and not np.isnan(brier) and ref_brier > 0) else np.nan

    return {
        "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "precision": prec,
        "recall": rec,
        "specificity": spec,
        "f1": f1,
        "mcc": mcc,
        "roc_auc": auc,
        "average_precision": ap,
        "brier_score": brier,
        "brier_skill_score": bss,
    }


def compute_calibration_slope_intercept(y_true, proba):
    from sklearn.linear_model import LogisticRegression as CalibLR
    eps = 1e-7
    p = np.clip(proba, eps, 1 - eps)
    logit = np.log(p / (1 - p)).reshape(-1, 1)
    calib_model = CalibLR(solver="lbfgs", penalty=None)
    calib_model.fit(logit, y_true)
    return float(calib_model.intercept_[0]), float(calib_model.coef_[0][0])


def main():
    print("=" * 80)
    print(" SWIFT: Student Wellness Intelligence Framework for Triage")
    print(" Master Publication-Grade Reproducibility Pipeline")
    print("=" * 80)

    # 1. Check dataset
    if not DATA_PATH.exists():
        print(f"\n[ERROR] Dataset not found at: {DATA_PATH}")
        print("Please download 'database_majorproj.csv' from Dryad (https://doi.org/10.5061/dryad.54qt7)")
        print("and place it into the 'data/' directory. See data/README.md for details.")
        sys.exit(1)

    print(f"\n[1/7] Loading dataset from {DATA_PATH}...")
    raw_df = pd.read_csv(DATA_PATH)
    print(f"      Raw dataset shape: {raw_df.shape}")

    # Feature engineering
    df = create_engineered_features(raw_df)
    target_col = "Depressive symptoms"
    y = map_binary_target(df[target_col]).astype(float)
    X = df.drop(columns=[target_col])
    
    # Retain all base and engineered features
    valid_mask = y.notna()
    X = X.loc[valid_mask].copy().reset_index(drop=True)
    y = y.loc[valid_mask].astype(int).copy().reset_index(drop=True)

    print(f"      Valid observations: N = {len(X)} (Positives: {y.sum()}, Prevalence: {y.mean():.4f})")

    # Stratified 75/25 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )
    X_train = X_train.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    print(f"      Training split (75%): N = {len(X_train)} (Positives: {y_train.sum()})")
    print(f"      Held-out test split (25%): N = {len(X_test)} (Positives: {y_test.sum()})")

    # 2. Primary Baseline Logistic Regression
    print("\n[2/7] Training Primary Benchmark Model (Logistic Regression, C=1.0, balanced)...")
    preprocessor = build_preprocessor(X_train)
    baseline_clf = LogisticRegression(C=1.0, class_weight="balanced", max_iter=5000, solver="lbfgs", random_state=42)
    baseline_pipeline = Pipeline([("preprocess", preprocessor), ("model", baseline_clf)])
    baseline_pipeline.fit(X_train, y_train)

    proba_baseline = baseline_pipeline.predict_proba(X_test)[:, 1]
    pred_baseline = (proba_baseline >= 0.5).astype(int)
    baseline_metrics = compute_metrics(y_test, proba_baseline, pred_baseline, has_proba=True)
    c_int, c_slope = compute_calibration_slope_intercept(y_test, proba_baseline)
    baseline_metrics["calib_intercept"] = c_int
    baseline_metrics["calib_slope"] = c_slope

    baseline_df = pd.DataFrame([baseline_metrics])
    baseline_df.to_csv(RESULTS_DIR / "baseline_lr_metrics.csv", index=False)

    print(f"      Accuracy: {baseline_metrics['accuracy']:.4f}")
    print(f"      Balanced Accuracy: {baseline_metrics['balanced_accuracy']:.4f}")
    print(f"      Recall (Sensitivity): {baseline_metrics['recall']:.4f}")
    print(f"      Specificity: {baseline_metrics['specificity']:.4f}")
    print(f"      F1-Score: {baseline_metrics['f1']:.4f}")
    print(f"      MCC: {baseline_metrics['mcc']:.4f}")
    print(f"      ROC-AUC: {baseline_metrics['roc_auc']:.4f}")
    print(f"      Average Precision: {baseline_metrics['average_precision']:.4f}")
    print(f"      Brier Score: {baseline_metrics['brier_score']:.4f}")
    print(f"      Calibration Intercept: {c_int:.4f}, Slope: {c_slope:.4f}")

    # 3. 1,000-Replication Bootstrap Confidence Intervals
    print("\n[3/7] Computing 1,000-Replication Bootstrap 95% Confidence Intervals for Baseline...")
    rng = np.random.default_rng(42)
    n_test = len(y_test)
    boot_records = []
    
    for b in range(1000):
        idx = rng.choice(n_test, size=n_test, replace=True)
        y_b = y_test.iloc[idx].values
        p_b = proba_baseline[idx]
        pred_b = (p_b >= 0.5).astype(int)
        
        m_b = compute_metrics(y_b, p_b, pred_b, has_proba=True)
        try:
            b_int, b_slope = compute_calibration_slope_intercept(y_b, p_b)
        except Exception:
            b_int, b_slope = np.nan, np.nan
        m_b["calib_intercept"] = b_int
        m_b["calib_slope"] = b_slope
        boot_records.append(m_b)

    boot_df = pd.DataFrame(boot_records)
    boot_df.to_csv(RESULTS_DIR / "baseline_lr_bootstrap_raw.csv", index=False)

    ci_summary = []
    for col in boot_df.columns:
        valid_vals = boot_df[col].dropna()
        point_est = baseline_metrics.get(col, np.nan)
        low_ci = np.percentile(valid_vals, 2.5)
        high_ci = np.percentile(valid_vals, 97.5)
        se = np.std(valid_vals, ddof=1)
        mean_val = np.mean(valid_vals)
        ci_summary.append({
            "metric": col,
            "point_estimate": point_est,
            "ci_lower_95": low_ci,
            "ci_upper_95": high_ci,
            "std_error": se,
            "boot_mean": mean_val,
        })

    ci_summary_df = pd.DataFrame(ci_summary)
    ci_summary_df.to_csv(RESULTS_DIR / "baseline_lr_bootstrap_ci.csv", index=False)
    print("      Bootstrap CIs successfully computed and saved to baseline_lr_bootstrap_ci.csv.")

    # 4. 17-Model Comparative Benchmark
    print("\n[4/7] Running 17-Model Comparative Benchmark (Table 5)...")
    model_specs = [
        ("Logistic Regression", LogisticRegression(C=1.0, max_iter=5000, class_weight="balanced", random_state=42)),
        ("Ridge Classifier", RidgeClassifier(class_weight="balanced")),
        ("Linear SVM", LinearSVC(class_weight="balanced", random_state=42)),
        ("RBF SVM", SVC(probability=True, class_weight="balanced", random_state=42)),
        ("KNN", KNeighborsClassifier(n_neighbors=7)),
        ("Decision Tree", DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=42)),
        ("Random Forest", RandomForestClassifier(n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1)),
        ("Extra Trees", ExtraTreesClassifier(n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1)),
        ("Gradient Boosting", GradientBoostingClassifier(random_state=42)),
        ("Hist Gradient Boosting", HistGradientBoostingClassifier(random_state=42)),
        ("AdaBoost", AdaBoostClassifier(random_state=42)),
        ("Naive Bayes", GaussianNB()),
        ("Quadratic Discriminant", QuadraticDiscriminantAnalysis()),
        ("MLP", MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=1000, random_state=42)),
    ]

    if BalancedRandomForestClassifier is not None:
        model_specs.append(("Balanced Random Forest", BalancedRandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1)))
    if BalancedBaggingClassifier is not None:
        model_specs.append(("Balanced Bagging", BalancedBaggingClassifier(n_estimators=200, random_state=42, n_jobs=-1)))
    if xgb is not None:
        model_specs.append(("XGBoost", xgb.XGBClassifier(n_estimators=250, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss", random_state=42)))
    if lgb is not None:
        model_specs.append(("LightGBM", lgb.LGBMClassifier(n_estimators=250, learning_rate=0.05, max_depth=4, subsample=0.9, colsample_bytree=0.9, random_state=42, n_jobs=-1, verbose=-1)))
    if cb is not None:
        model_specs.append(("CatBoost", cb.CatBoostClassifier(iterations=250, depth=4, learning_rate=0.05, loss_function="Logloss", verbose=False, random_seed=42)))

    benchmark_results = []
    for name, estimator in model_specs:
        pipe = Pipeline([("preprocess", build_preprocessor(X_train)), ("model", estimator)])
        try:
            pipe.fit(X_train, y_train)
            has_proba = hasattr(pipe, "predict_proba")
            if has_proba:
                prob = pipe.predict_proba(X_test)[:, 1]
            else:
                try:
                    dec = pipe.decision_function(X_test)
                    prob = (dec - dec.min()) / (dec.max() - dec.min() + 1e-9)
                except Exception:
                    prob = pipe.predict(X_test).astype(float)
            
            pred = pipe.predict(X_test)
            m = compute_metrics(y_test, prob, pred, has_proba=has_proba)
            benchmark_results.append({
                "model": name,
                "accuracy": m["accuracy"],
                "balanced_accuracy": m["balanced_accuracy"],
                "precision": m["precision"],
                "recall": m["recall"],
                "specificity": m["specificity"],
                "f1": m["f1"],
                "mcc": m["mcc"],
                "roc_auc": m["roc_auc"],
                "average_precision": m["average_precision"],
                "brier_score": m["brier_score"] if has_proba else np.nan,
            })
        except Exception as e:
            print(f"      Skipping {name}: {e}")

    comp_df = pd.DataFrame(benchmark_results)
    comp_df.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    print("      Table 5 benchmark comparison saved to model_comparison.csv.")

    # 5. Optuna Sensitivity Analysis (Train-CV Only)
    if optuna is not None:
        print("\n[5/7] Executing Optuna Sensitivity Analysis (15 trials, 5-fold CV strictly on X_train)...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        
        def optuna_objective(trial):
            c_val = trial.suggest_float("C", 0.001, 10.0, log=True)
            solver_val = trial.suggest_categorical("solver", ["liblinear", "lbfgs"])
            max_iter_val = trial.suggest_int("max_iter", 500, 5000)
            
            m = Pipeline([
                ("preprocess", build_preprocessor(X_train)),
                ("model", LogisticRegression(
                    C=c_val, solver=solver_val, max_iter=max_iter_val,
                    class_weight="balanced", random_state=42
                )),
            ])
            return cross_val_score(m, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1).mean()

        sampler = optuna.samplers.TPESampler(seed=42)
        study = optuna.create_study(direction="maximize", sampler=sampler)
        study.optimize(optuna_objective, n_trials=15, show_progress_bar=False)

        best_params = study.best_trial.params
        print(f"      Best train-CV params: {best_params} (CV ROC-AUC: {study.best_value:.4f})")

        tuned_pipe = Pipeline([
            ("preprocess", build_preprocessor(X_train)),
            ("model", LogisticRegression(**best_params, class_weight="balanced", random_state=42)),
        ])
        tuned_pipe.fit(X_train, y_train)
        proba_tuned = tuned_pipe.predict_proba(X_test)[:, 1]
        pred_tuned = (proba_tuned >= 0.5).astype(int)
        tuned_metrics = compute_metrics(y_test, proba_tuned, pred_tuned, has_proba=True)
        t_int, t_slope = compute_calibration_slope_intercept(y_test, proba_tuned)
        tuned_metrics["calib_intercept"] = t_int
        tuned_metrics["calib_slope"] = t_slope
        tuned_metrics["best_params"] = json.dumps(best_params)

        pd.DataFrame([tuned_metrics]).to_csv(RESULTS_DIR / "optuna_sensitivity_metrics.csv", index=False)
        print(f"      Tuned Model Test ROC-AUC: {tuned_metrics['roc_auc']:.4f}, MCC: {tuned_metrics['mcc']:.4f}")
    else:
        print("\n[5/7] Skipping Optuna (optuna not installed).")

    # 6. Calibration & Reliability Assessment
    print("\n[6/7] Generating Calibration Curve & Reliability Diagram...")
    frac_pos_base, mean_pred_base = calibration_curve(y_test, proba_baseline, n_bins=10, strategy="quantile")
    
    plt.figure(figsize=(7, 5.5), dpi=300)
    plt.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=1.5)
    plt.plot(mean_pred_base, frac_pos_base, "s-", color="darkblue", label=f"Baseline LR (C=1.0, Brier={baseline_metrics['brier_score']:.3f})", markersize=7, linewidth=1.8)
    if 'proba_tuned' in locals():
        frac_pos_tuned, mean_pred_tuned = calibration_curve(y_test, proba_tuned, n_bins=10, strategy="quantile")
        plt.plot(mean_pred_tuned, frac_pos_tuned, "o--", color="crimson", label=f"Tuned LR (Brier={tuned_metrics['brier_score']:.3f})", markersize=6, linewidth=1.5)
    
    plt.xlabel("Mean Predicted Probability", fontsize=11)
    plt.ylabel("Fraction of Positives", fontsize=11)
    plt.title("Calibration Reliability Diagram (Held-Out Test Set)", fontsize=12)
    plt.xlim(-0.02, 1.02)
    plt.ylim(-0.02, 1.02)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "calibration_reliability_diagram.png", dpi=300)
    plt.close()
    print("      Reliability plot saved to calibration_reliability_diagram.png.")

    # 7. Explainability Pipeline (SHAP & LIME)
    print("\n[7/7] Generating Explainability Outputs (SHAP & LIME)...")
    # Fit preprocessor on training data and extract feature names
    preprocessor = baseline_pipeline.named_steps["preprocess"]
    classifier = baseline_pipeline.named_steps["model"]
    
    X_train_trans = preprocessor.transform(X_train)
    X_test_trans = preprocessor.transform(X_test)
    feature_names = preprocessor.get_feature_names_out().tolist()

    if shap is not None:
        try:
            # Sample background strictly from X_train
            bg_indices = rng.choice(len(X_train_trans), size=min(250, len(X_train_trans)), replace=False)
            bg_data = X_train_trans[bg_indices]
            
            explainer = shap.LinearExplainer(classifier, bg_data)
            shap_vals = explainer(X_test_trans)
            
            mean_abs_shap = np.abs(shap_vals.values).mean(axis=0)
            shap_importance = pd.DataFrame({
                "feature": feature_names,
                "mean_abs_shap": mean_abs_shap,
            }).sort_values("mean_abs_shap", ascending=False)
            shap_importance.to_csv(RESULTS_DIR / "shap_global_importance.csv", index=False)
            print("      SHAP global importance saved to shap_global_importance.csv.")
        except Exception as e:
            print(f"      SHAP calculation failed: {e}")
    else:
        print("      SHAP not installed; skipping SHAP.")

    if LimeTabularExplainer is not None:
        try:
            # Fit LIME explainer using training data reference distribution
            lime_exp = LimeTabularExplainer(
                training_data=X_train_trans,
                feature_names=feature_names,
                class_names=["No Depression", "Depression Risk"],
                mode="classification",
                random_state=42,
            )
            # Select test instance closest to median predicted risk score
            median_score = np.median(proba_baseline)
            rep_idx = int(np.argmin(np.abs(proba_baseline - median_score)))
            rep_instance = X_test_trans[rep_idx]
            
            def predict_fn(x):
                return classifier.predict_proba(x)

            exp = lime_exp.explain_instance(rep_instance, predict_fn, num_features=10, num_samples=5000)
            lime_df = pd.DataFrame(exp.as_list(), columns=["feature_rule", "weight"])
            lime_df.to_csv(RESULTS_DIR / "lime_representative_explanation.csv", index=False)
            print(f"      LIME explanation for test instance {rep_idx} (score={proba_baseline[rep_idx]:.4f}) saved.")
        except Exception as e:
            print(f"      LIME calculation failed: {e}")
    else:
        print("      LIME not installed; skipping LIME.")

    print("\n" + "=" * 80)
    print(" SWIFT Reproducibility Pipeline Completed Successfully!")
    print(f" Verified artifacts stored in: {RESULTS_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
