"""Clinical feature engineering for passive EHR screening."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _yes_no(value) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"yes", "y", "true", "1"}:
            return "yes"
        if v in {"no", "n", "false", "0"}:
            return "no"
    return str(value)


def compute_engineered_features(row: dict) -> dict:
    height_m = row.get("height_m") or (row.get("Height (cm)", np.nan) / 100.0)
    weight = row.get("weight_kg") or row.get("Weight (kg)", np.nan)
    sbp = row.get("systolic_blood_pressure_mmhg") or row.get("Systolic blood pressure (mmHg)", np.nan)
    dbp = row.get("diastolic_blood_pressure_mmhg") or row.get("Diastolic blood pressure (mmHg)", np.nan)
    hr = row.get("heart_rate_bpm") or row.get("Heart rate (bpm)", np.nan)

    bmi = weight / (height_m ** 2) if height_m and weight else np.nan
    sbp_dbp_ratio = sbp / dbp if sbp and dbp else np.nan
    heart_rate_bmi_ratio = hr / bmi if hr and bmi else np.nan

    if pd.notna(bmi):
        if bmi < 18.5:
            bmi_cat = "underweight"
        elif bmi < 25:
            bmi_cat = "normal"
        elif bmi < 30:
            bmi_cat = "overweight"
        else:
            bmi_cat = "obese"
    else:
        bmi_cat = "normal"

    if pd.notna(sbp):
        if sbp <= 120:
            bp_cat = "normal"
        elif sbp <= 139:
            bp_cat = "elevated"
        elif sbp <= 159:
            bp_cat = "stage1"
        else:
            bp_cat = "stage2"
    else:
        bp_cat = "normal"

    return {
        "height_m": height_m,
        "bmi": bmi,
        "sbp_dbp_ratio": sbp_dbp_ratio,
        "heart_rate_bmi_ratio": heart_rate_bmi_ratio,
        "bmi_cat": bmi_cat,
        "bp_cat": bp_cat,
    }
