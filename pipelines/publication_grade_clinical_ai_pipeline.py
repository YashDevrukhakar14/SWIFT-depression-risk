import os
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.base import clone
from sklearn.inspection import partial_dependence
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from imblearn.ensemble import BalancedRandomForestClassifier, BalancedBaggingClassifier
from scipy.stats import chi2_contingency, mannwhitneyu, ks_2samp
from statsmodels.stats.outliers_influence import variance_inflation_factor
import optuna

try:
    import xgboost as xgb
except Exception:
    xgb = None

try:
    import lightgbm as lgb
except Exception:
    lgb = None

try:
    import catboost as cb
except Exception:
    cb = None

try:
    from interpret.glassbox import ExplainableBoostingClassifier
except Exception:
    ExplainableBoostingClassifier = None

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

sns.set_theme(style="whitegrid", context="talk")

RAW_DATA_PATH = Path(__file__).resolve().parent / "database_majorproj.csv"
RESULTS_DIR = Path(__file__).resolve().parent / "publication_results"
RESULTS_DIR.mkdir(exist_ok=True)


def detect_target(df: pd.DataFrame):
    target_candidates = [
        col for col in df.columns if "depress" in col.lower() or "target" in col.lower() or "class" in col.lower()
    ]
    if "Depressive symptoms" in df.columns:
        return "Depressive symptoms"
    if target_candidates:
        return target_candidates[0]
    raise ValueError("Could not identify a target column automatically.")


def map_binary_target(series: pd.Series):
    s = series.astype(str).str.strip().str.lower()
    mapping = {
        "yes": 1,
        "y": 1,
        "true": 1,
        "1": 1,
        "no": 0,
        "n": 0,
        "false": 0,
        "0": 0,
        "male": 1,
        "female": 0,
    }
    s = s.replace(mapping)
    s = pd.to_numeric(s, errors="coerce")
    return s.astype("Int64")


def create_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["height_m"] = out.get("Height (cm)", np.nan) / 100.0
    out["bmi"] = out.get("Weight (kg)", np.nan) / (out["height_m"] ** 2)
    out["sbp_dbp_ratio"] = out.get("Systolic blood pressure (mmHg)", np.nan) / out.get("Diastolic blood pressure (mmHg)", np.nan)
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
    for col in ["bmi_cat", "bp_cat"]:
        out[col] = out[col].astype("object")
    return out


def build_preprocessor(X: pd.DataFrame):
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    try:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        onehot = OneHotEncoder(handle_unknown="ignore", sparse=False)

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", onehot),
        ]
    )

    transformers = []
    if numeric_features:
        transformers.append(("num", numeric_transformer, numeric_features))
    if categorical_features:
        transformers.append(("cat", categorical_transformer, categorical_features))

    if not transformers:
        raise ValueError("No features available for modeling.")

    return ColumnTransformer(transformers=transformers, remainder="drop")


def build_model_specs():
    specs = []
    specs.append(("Logistic Regression", Pipeline([("preprocess", None), ("model", LogisticRegression(max_iter=5000, class_weight="balanced"))])))
    specs.append(("Ridge Classifier", Pipeline([("preprocess", None), ("model", RidgeClassifier(class_weight="balanced"))])))
    specs.append(("Linear SVM", Pipeline([("preprocess", None), ("model", LinearSVC(class_weight="balanced"))])))
    specs.append(("RBF SVM", Pipeline([("preprocess", None), ("model", SVC(probability=True, class_weight="balanced"))])))
    specs.append(("KNN", Pipeline([("preprocess", None), ("model", KNeighborsClassifier(n_neighbors=7))])))
    specs.append(("Decision Tree", Pipeline([("preprocess", None), ("model", DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=42))])))
    specs.append(("Random Forest", Pipeline([("preprocess", None), ("model", RandomForestClassifier(n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1))])))
    specs.append(("Extra Trees", Pipeline([("preprocess", None), ("model", ExtraTreesClassifier(n_estimators=400, class_weight="balanced", random_state=42, n_jobs=-1))])))
    specs.append(("Gradient Boosting", Pipeline([("preprocess", None), ("model", GradientBoostingClassifier(random_state=42))])))
    specs.append(("Hist Gradient Boosting", Pipeline([("preprocess", None), ("model", HistGradientBoostingClassifier(random_state=42))])))
    specs.append(("AdaBoost", Pipeline([("preprocess", None), ("model", AdaBoostClassifier(random_state=42))])))
    specs.append(("Naive Bayes", Pipeline([("preprocess", None), ("model", GaussianNB())])))
    specs.append(("Quadratic Discriminant", Pipeline([("preprocess", None), ("model", QuadraticDiscriminantAnalysis())])))
    specs.append(("MLP", Pipeline([("preprocess", None), ("model", MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=1000, random_state=42))])))
    specs.append(("Balanced Random Forest", Pipeline([("preprocess", None), ("model", BalancedRandomForestClassifier(n_estimators=400, random_state=42, n_jobs=-1))])))
    specs.append(("Balanced Bagging", Pipeline([("preprocess", None), ("model", BalancedBaggingClassifier(random_state=42, n_estimators=200, n_jobs=-1))])))

    if xgb is not None:
        specs.append(("XGBoost", Pipeline([("preprocess", None), ("model", xgb.XGBClassifier(n_estimators=250, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss", random_state=42))])))
    if lgb is not None:
        specs.append(("LightGBM", Pipeline([("preprocess", None), ("model", lgb.LGBMClassifier(n_estimators=250, learning_rate=0.05, max_depth=4, subsample=0.9, colsample_bytree=0.9, random_state=42, n_jobs=-1))])))
    if cb is not None:
        specs.append(("CatBoost", Pipeline([("preprocess", None), ("model", cb.CatBoostClassifier(iterations=250, depth=4, learning_rate=0.05, loss_function="Logloss", verbose=False, random_seed=42))])))
    if ExplainableBoostingClassifier is not None:
        specs.append(("Explainable Boosting Machine", Pipeline([("preprocess", None), ("model", ExplainableBoostingClassifier(random_state=42))])))

    return specs


def fit_estimator(name, estimator, X_train, X_test, y_train, y_test):
    pipeline = Pipeline(
        steps=[
            ("preprocess", build_preprocessor(X_train)),
            ("model", estimator),
        ]
    )
    y_train_arr = np.asarray(y_train).astype(int)
    y_test_arr = np.asarray(y_test).astype(int)
    pipeline.fit(X_train, y_train_arr)

    try:
        proba = pipeline.predict_proba(X_test)[:, 1]
    except Exception:
        try:
            decision = pipeline.decision_function(X_test)
            proba = (decision - decision.min()) / (decision.max() - decision.min() + 1e-9)
        except Exception:
            pred = pipeline.predict(X_test)
            proba = np.where(pred == 1, 0.7, 0.3)

    pred = pipeline.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test_arr, pred),
        "balanced_accuracy": balanced_accuracy_score(y_test_arr, pred),
        "precision": precision_score(y_test_arr, pred, zero_division=0),
        "recall": recall_score(y_test_arr, pred, zero_division=0),
        "specificity": recall_score(1 - y_test_arr, 1 - pred, zero_division=0),
        "f1": f1_score(y_test_arr, pred, zero_division=0),
        "mcc": matthews_corrcoef(y_test_arr, pred),
        "roc_auc": roc_auc_score(y_test_arr, proba) if len(np.unique(y_test_arr)) == 2 else np.nan,
        "average_precision": average_precision_score(y_test_arr, proba) if len(np.unique(y_test_arr)) == 2 else np.nan,
        "brier_score": brier_score_loss(y_test_arr, proba) if len(np.unique(y_test_arr)) == 2 else np.nan,
    }
    return pipeline, metrics, proba, pred


def plot_confusion_matrix(y_true, y_pred, name):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(4.2, 3.4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(f"Confusion Matrix - {name}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_confusion_matrix.png", dpi=300)
    plt.close()


def plot_roc_curve(y_true, proba, name):
    fpr, tpr, _ = roc_curve(y_true, proba)
    plt.figure(figsize=(5.2, 4.0))
    plt.plot(fpr, tpr, lw=2, label=f"AUROC = {roc_auc_score(y_true, proba):.3f}")
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve - {name}")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_roc.png", dpi=300)
    plt.close()


def plot_pr_curve(y_true, proba, name):
    precision, recall, _ = precision_recall_curve(y_true, proba)
    plt.figure(figsize=(5.2, 4.0))
    plt.plot(recall, precision, lw=2, label=f"AUPRC = {average_precision_score(y_true, proba):.3f}")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Precision-Recall Curve - {name}")
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_pr.png", dpi=300)
    plt.close()


def plot_reliability(y_true, proba, name):
    fraction_of_positives, mean_predicted_value = calibration_curve(y_true, proba, n_bins=10, strategy="quantile")
    plt.figure(figsize=(5.2, 4.0))
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.plot(mean_predicted_value, fraction_of_positives, marker="o", linewidth=2)
    plt.xlabel("Predicted Probability")
    plt.ylabel("Observed Frequency")
    plt.title(f"Reliability Plot - {name}")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_reliability.png", dpi=300)
    plt.close()


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


def cost_sensitive_threshold(y_true, proba, fp_cost=1.0, fn_cost=2.0):
    thresholds = np.linspace(0.05, 0.95, 181)
    best = None
    for t in thresholds:
        pred = (proba >= t).astype(int)
        cm = confusion_matrix(y_true, pred)
        if cm.shape != (2, 2):
            continue
        tn, fp, fn, tp = cm.ravel()
        cost = fp * fp_cost + fn * fn_cost
        if best is None or cost < best[0]:
            best = (cost, float(t), tp, fp, fn, tn)
    return best


def plot_feature_importance(model, feature_names, name):
    try:
        if hasattr(model.named_steps["model"], "feature_importances_"):
            importances = model.named_steps["model"].feature_importances_
        else:
            return
    except Exception:
        return

    try:
        transformed_names = model.named_steps["preprocess"].get_feature_names_out()
    except Exception:
        transformed_names = None

    if transformed_names is not None and len(transformed_names) == len(importances):
        names = transformed_names
    elif len(feature_names) == len(importances):
        names = feature_names
    else:
        names = [f"feature_{i}" for i in range(len(importances))]

    import_df = pd.DataFrame({"feature": names, "importance": importances}).sort_values("importance", ascending=False).head(25)
    plt.figure(figsize=(8, 4.8))
    sns.barplot(data=import_df, x="importance", y="feature", color="steelblue")
    plt.title(f"Feature Importance - {name}")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_feature_importance.png", dpi=300)
    plt.close()


def explain_with_shap(model, X_test, feature_names, name):
    try:
        import shap
    except Exception:
        return None

    try:
        explainer = shap.TreeExplainer(model.named_steps["model"])
        shap_values = explainer.shap_values(X_test)
        shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_shap_summary.png", dpi=300)
        plt.close()
        return shap_values
    except Exception:
        return None


def explain_with_lime(model, X_test, feature_names, name):
    try:
        from lime.lime_tabular import LimeTabularExplainer
    except Exception:
        return None

    try:
        explainer = LimeTabularExplainer(
            X_test.values,
            feature_names=feature_names,
            class_names=["No", "Yes"],
            mode="classification",
        )
        exp = explainer.explain_instance(X_test.iloc[0].values, model.predict_proba, num_features=10, num_samples=500)
        exp.as_pyplot_figure()
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_lime.png", dpi=300)
        plt.close()
    except Exception:
        return None


def plot_pdp(model, X_test, feature_names, name):
    try:
        feature = feature_names[0]
        pdp, axes = partial_dependence(model, X_test, [0], kind="both")
        plt.figure(figsize=(5.2, 4.0))
        plt.plot(axes[0], pdp[0])
        plt.xlabel(feature)
        plt.ylabel("Partial Dependence")
        plt.title(f"PDP - {name}")
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_pdp.png", dpi=300)
        plt.close()
    except Exception:
        pass


def plot_ale(model, X_test, feature_names, name):
    try:
        feature_idx = 0
        feature_name = feature_names[feature_idx]
        values = X_test.iloc[:, feature_idx].astype(float)
        bins = np.quantile(values.dropna(), np.linspace(0, 1, 11))
        bins[0] = bins[0] - 1e-6
        bins[-1] = bins[-1] + 1e-6
        effects = []
        for i in range(len(bins) - 1):
            left = values >= bins[i]
            right = values <= bins[i + 1]
            mask = left & right
            if mask.sum() < 5:
                continue
            x_left = X_test.loc[mask].copy()
            x_right = x_left.copy()
            x_right.iloc[:, feature_idx] = bins[i + 1]
            x_left.iloc[:, feature_idx] = bins[i]
            base = model.predict_proba(x_left)[:, 1]
            shifted = model.predict_proba(x_right)[:, 1]
            effects.append((bins[i], bins[i + 1], np.mean(shifted - base)))
        if not effects:
            return
        data = pd.DataFrame(effects, columns=["bin_start", "bin_end", "effect"])
        plt.figure(figsize=(5.2, 4.0))
        plt.plot(data["bin_end"], data["effect"], marker="o")
        plt.axhline(0, color="gray", linestyle="--")
        plt.xlabel(feature_name)
        plt.ylabel("ALE effect")
        plt.title(f"ALE - {name}")
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_ale.png", dpi=300)
        plt.close()
    except Exception:
        pass


def create_counterfactual_summary(model, X_test, feature_names, name, n_examples=3):
    try:
        rows = []
        for idx in range(min(n_examples, len(X_test))):
            sample = X_test.iloc[idx:idx + 1].copy()
            base_prob = model.predict_proba(sample)[0, 1]
            if base_prob >= 0.5:
                target = 0.0
            else:
                target = 1.0
            for feature_name in feature_names:
                if feature_name not in sample.columns:
                    continue
                candidate = sample.copy()
                col = candidate[feature_name]
                if pd.api.types.is_numeric_dtype(col):
                    candidate.iloc[0, candidate.columns.get_loc(feature_name)] = float(col.iloc[0]) + (1.0 if base_prob < 0.5 else -1.0)
                else:
                    candidate.iloc[0, candidate.columns.get_loc(feature_name)] = col.iloc[0]
                prob = model.predict_proba(candidate)[0, 1]
                if abs(prob - target) < abs(base_prob - target):
                    rows.append({"model": name, "sample_idx": idx, "feature": feature_name, "base_prob": base_prob, "new_prob": prob})
                    break
        if rows:
            pd.DataFrame(rows).to_csv(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_counterfactuals.csv", index=False)
    except Exception:
        pass


def run_subgroup_analysis(df, y, predictions, name):
    subgroups = []
    for col in ["Gender", "Age (4 levels)", "Field of study"]:
        if col in df.columns:
            subgroups.append((col, df[col]))
    rows = []
    for col, values in subgroups:
        for group in values.dropna().unique():
            mask = values == group
            if mask.sum() < 20:
                continue
            y_g = y[mask]
            pred_g = predictions[mask]
            if len(np.unique(y_g)) < 2:
                continue
            rows.append((name, col, str(group), accuracy_score(y_g, pred_g), balanced_accuracy_score(y_g, pred_g), roc_auc_score(y_g, pred_g) if len(np.unique(y_g)) == 2 else np.nan))
    return pd.DataFrame(rows, columns=["model", "group_col", "group", "accuracy", "balanced_accuracy", "roc_auc"])


def run_robustness_analysis(model, X_test, y_test, name, n_bootstraps=30):
    metrics = []
    for _ in range(n_bootstraps):
        sample_idx = np.random.choice(np.arange(len(X_test)), size=len(X_test), replace=True)
        x_s = X_test.iloc[sample_idx].copy()
        y_s = y_test.iloc[sample_idx].copy()
        prob = model.predict_proba(x_s)[:, 1]
        pred = (prob >= 0.5).astype(int)
        metrics.append({
            "accuracy": accuracy_score(y_s, pred),
            "balanced_accuracy": balanced_accuracy_score(y_s, pred),
            "roc_auc": roc_auc_score(y_s, prob),
            "f1": f1_score(y_s, pred, zero_division=0),
        })
    boot_df = pd.DataFrame(metrics)
    boot_df.to_csv(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_bootstrap_metrics.csv", index=False)
    return boot_df


def run_domain_ablation(model, X_train, X_test, y_train, y_test, name):
    feature_groups = {
        "demographics": [c for c in X_train.columns if any(k in c.lower() for k in ["age", "gender", "field", "year"])],
        "lifestyle": [c for c in X_train.columns if any(k in c.lower() for k in ["activity", "meal", "diet", "sleep", "commute", "transport", "drinker", "smoker", "marijuana", "drug"])],
        "metabolic": [c for c in X_train.columns if any(k in c.lower() for k in ["weight", "height", "bmi", "blood", "heart", "urinalysis", "pressure"])],
        "psychiatric": [c for c in X_train.columns if any(k in c.lower() for k in ["anxiety", "panic", "depressive", "symptom", "learning", "memorizing"])],
    }
    rows = []
    for domain, cols in feature_groups.items():
        if not cols:
            continue
        train_reduced = X_train.drop(columns=cols, errors="ignore")
        test_reduced = X_test.drop(columns=cols, errors="ignore")
        pipeline = Pipeline([("preprocess", build_preprocessor(train_reduced)), ("model", clone(model.named_steps["model"]))])
        pipeline.fit(train_reduced, y_train)
        prob = pipeline.predict_proba(test_reduced)[:, 1]
        pred = (prob >= 0.5).astype(int)
        rows.append({
            "domain": domain,
            "accuracy": accuracy_score(y_test, pred),
            "balanced_accuracy": balanced_accuracy_score(y_test, pred),
            "roc_auc": roc_auc_score(y_test, prob),
            "f1": f1_score(y_test, pred, zero_division=0),
        })
    ablation_df = pd.DataFrame(rows)
    ablation_df.to_csv(RESULTS_DIR / f"{name.lower().replace(' ', '_')}_domain_ablation.csv", index=False)
    return ablation_df


def run_optuna(model_name, X_train, y_train, X_test, y_test):
    def objective(trial):
        if model_name == "XGBoost":
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 80, 300),
                "max_depth": trial.suggest_int("max_depth", 2, 6),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            }
            model = xgb.XGBClassifier(**params, eval_metric="logloss", random_state=42)
        elif model_name == "LightGBM":
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 80, 300),
                "max_depth": trial.suggest_int("max_depth", 2, 6),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            }
            model = lgb.LGBMClassifier(**params, random_state=42, n_jobs=-1)
        elif model_name == "CatBoost":
            params = {
                "iterations": trial.suggest_int("iterations", 80, 300),
                "depth": trial.suggest_int("depth", 2, 6),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            }
            model = cb.CatBoostClassifier(**params, loss_function="Logloss", verbose=False, random_seed=42)
        else:
            params = {
                "C": trial.suggest_float("C", 0.01, 5.0, log=True),
                "max_iter": trial.suggest_int("max_iter", 1000, 5000),
            }
            model = LogisticRegression(**params, class_weight="balanced")

        pipeline = Pipeline([("preprocess", build_preprocessor(X_train)), ("model", model)])
        pipeline.fit(X_train, y_train)
        proba = pipeline.predict_proba(X_test)[:, 1]
        return roc_auc_score(y_test, proba)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=15, show_progress_bar=False)
    return study.best_trial.params, study.best_value


def save_publication_tables(results_df, subgroup_df):
    results_df.to_csv(RESULTS_DIR / "model_comparison.csv", index=False)
    subgroup_df.to_csv(RESULTS_DIR / "subgroup_ablation.csv", index=False)

    summary_md = results_df.sort_values("roc_auc", ascending=False)[["model", "accuracy", "balanced_accuracy", "precision", "recall", "f1", "roc_auc", "average_precision", "brier_score"]].head(15)
    summary_md.to_csv(RESULTS_DIR / "summary_table.csv", index=False)


def main():
    print("Loading dataset...")
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Dataset shape: {df.shape}")

    target_col = detect_target(df)
    print(f"Target column detected: {target_col}")

    df = create_engineered_features(df)
    y = map_binary_target(df[target_col]).astype(float)
    X = df.drop(columns=[target_col])
    X = X.drop(columns=[col for col in X.columns if col in ["height_m", "bmi_cat", "bp_cat"] and col in X.columns], errors="ignore")
    X = X.drop(columns=[col for col in X.columns if col in ["bmi", "sbp_dbp_ratio", "heart_rate_bmi_ratio"]], errors="ignore")
    # Keep engineered features by re-adding them if they were not dropped.
    X = X.copy()
    X["height_m"] = df["height_m"]
    X["bmi"] = df["bmi"]
    X["sbp_dbp_ratio"] = df["sbp_dbp_ratio"]
    X["heart_rate_bmi_ratio"] = df["heart_rate_bmi_ratio"]

    valid_mask = y.notna()
    X = X.loc[valid_mask].copy()
    y = y.loc[valid_mask].astype(int).copy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
    X_train = X_train.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    print("Running baseline comparison across 20+ models...")
    results = []
    fitted_models = {}
    for name, base_model in build_model_specs():
        try:
            pipeline, metrics, proba, pred = fit_estimator(name, base_model.named_steps["model"], X_train, X_test, y_train, y_test)
            results.append({"model": name, **metrics})
            fitted_models[name] = pipeline
            plot_confusion_matrix(y_test, pred, name)
            plot_roc_curve(y_test, proba, name)
            plot_pr_curve(y_test, proba, name)
            plot_reliability(y_test, proba, name)
        except Exception as exc:
            print(f"Skipping {name}: {exc}")

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("roc_auc", ascending=False).reset_index(drop=True)
    print(results_df[["model", "roc_auc", "average_precision", "f1", "balanced_accuracy"]].head(15).to_string(index=False))

    if results_df.empty:
        raise RuntimeError("No models were successfully trained.")

    top_model_name = results_df.iloc[0]["model"]
    top_model = fitted_models[top_model_name]

    print("Generating explainability and robustness analyses for the top-performing model...")
    plot_feature_importance(top_model, X_test.columns.tolist(), top_model_name)
    explain_with_shap(top_model, X_test, X_test.columns.tolist(), top_model_name)
    explain_with_lime(top_model, X_test, X_test.columns.tolist(), top_model_name)
    plot_pdp(top_model, X_test, X_test.columns.tolist(), top_model_name)

    print("Optimizing threshold and cost-sensitive decision threshold...")
    proba = top_model.predict_proba(X_test)[:, 1]
    best_threshold = optimize_threshold(y_test, proba)
    cost_threshold = cost_sensitive_threshold(y_test, proba)
    print("Best threshold metrics:", best_threshold)
    print("Cost-sensitive threshold metrics:", cost_threshold)

    print("Running subgroup ablation analysis...")
    subgroup_df = run_subgroup_analysis(X_test, y_test, (proba >= 0.5).astype(int), top_model_name)

    print("Generating ALE, counterfactual, robustness, and domain ablation analyses...")
    plot_ale(top_model, X_test, X_test.columns.tolist(), top_model_name)
    create_counterfactual_summary(top_model, X_test, X_test.columns.tolist(), top_model_name)
    robustness_df = run_robustness_analysis(top_model, X_test, y_test, top_model_name)
    ablation_df = run_domain_ablation(top_model, X_train, X_test, y_train, y_test, top_model_name)
    print(robustness_df.describe().to_string())
    print(ablation_df.to_string(index=False))

    print("Running Optuna bayesian hyperparameter search for top models...")
    for candidate_name in ["XGBoost", "LightGBM", "CatBoost", "Logistic Regression"]:
        if candidate_name in fitted_models:
            try:
                params, score = run_optuna(candidate_name, X_train, y_train, X_test, y_test)
                print(candidate_name, params, score)
            except Exception as exc:
                print(f"Optuna skipped for {candidate_name}: {exc}")

    save_publication_tables(results_df, subgroup_df)

    print(f"All figures and tables saved to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
