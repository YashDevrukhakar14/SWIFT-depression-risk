"""Generate optional SHAP explanations for the trained SWIFT model."""

from pathlib import Path

import joblib
import pandas as pd

from feature_engineering import prepare_xy

ROOT = Path(__file__).resolve().parent


def main():
    try:
        import shap
    except ImportError as exc:
        raise SystemExit("Install requirements.txt before running XAI evaluation.") from exc

    model = joblib.load(ROOT / "artifacts" / "swift_model.joblib")
    features, _ = prepare_xy(pd.read_csv(ROOT / "database_majorproj.csv"))
    sample = features.sample(min(250, len(features)), random_state=42)
    transformed = model.named_steps["preprocess"].transform(sample)
    names = model.named_steps["preprocess"].get_feature_names_out()
    explainer = shap.LinearExplainer(model.named_steps["model"], transformed)
    values = explainer(transformed)
    importance = pd.DataFrame({"feature": names, "mean_abs_shap": abs(values.values).mean(axis=0)})
    importance.sort_values("mean_abs_shap", ascending=False).to_csv(ROOT / "artifacts" / "shap_importance.csv", index=False)
    print(importance.sort_values("mean_abs_shap", ascending=False).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
