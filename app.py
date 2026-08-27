"""Minimal Streamlit interface for the trained SWIFT model."""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from feature_engineering import prepare_xy

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "artifacts" / "swift_model.joblib"

st.set_page_config(page_title="SWIFT Risk Estimation", page_icon="S")
st.title("SWIFT: Student Wellness Depression-Risk Estimation")
st.caption("Decision-support estimate, not a clinical diagnosis.")

if not MODEL_PATH.exists():
    st.error("Model artifact not found. Run: python train.py")
    st.stop()

model = joblib.load(MODEL_PATH)
features, _ = prepare_xy(pd.read_csv(ROOT / "database_majorproj.csv"))
row = {}
for column in features.columns:
    series = features[column]
    if pd.api.types.is_numeric_dtype(series):
        row[column] = st.number_input(column, value=float(series.median()))
    else:
        choices = sorted(series.dropna().astype(str).unique().tolist())
        row[column] = st.selectbox(column, choices, index=0) if choices else ""

if st.button("Estimate risk", type="primary"):
    probability = float(model.predict_proba(pd.DataFrame([row]))[0, 1])
    st.metric("Estimated risk probability", f"{probability:.1%}")
    st.info("This estimate is intended to support further assessment and should not replace professional judgment.")
