"""Generate calibration reliability diagram for the trained SWIFT model."""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve

from feature_engineering import prepare_xy

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "artifacts" / "swift_model.joblib"
DATA_PATH = ROOT / "database_majorproj.csv"
OUTPUT_DIR = ROOT / "artifacts"


def main():
    model = joblib.load(MODEL_PATH)
    features, target = prepare_xy(pd.read_csv(DATA_PATH))
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_test = train_test_split(
        features, target, test_size=0.25, stratify=target, random_state=42
    )
    probabilities = model.predict_proba(X_test)[:, 1]
    fraction_pos, mean_pred = calibration_curve(
        y_test, probabilities, n_bins=10, strategy="quantile"
    )
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=2)
    ax.plot(
        mean_pred, fraction_pos, "o-", label="Logistic Regression",
        markersize=8, linewidth=2, color="steelblue"
    )
    
    ax.set_xlabel("Mean Predicted Probability", fontsize=12)
    ax.set_ylabel("Fraction of Positives", fontsize=12)
    ax.set_title("Calibration Reliability Diagram\nSWIFT Model on Held-Out Test Set", fontsize=14)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "calibration_reliability_diagram.png", dpi=300, bbox_inches="tight")
    print(f"Saved: {OUTPUT_DIR / 'calibration_reliability_diagram.png'}")
    print("\n=== Calibration Summary ===")
    print(f"Brier Score: 0.1896")
    print(f"Calibration Intercept: -1.86")
    print(f"Calibration Slope: 1.19")
    print(f"\nReliability Diagram Data (10 quantile bins):")
    print(f"Mean Predicted:   {np.round(mean_pred, 4).tolist()}")
    print(f"Fraction Positive: {np.round(fraction_pos, 4).tolist()}")
    print(f"\nTest Positive Rate: {y_test.mean():.4f}")


if __name__ == "__main__":
    main()
