"""Shared feature engineering and preprocessing helpers for SWIFT."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "Depressive symptoms"
ENGINEERED_COLUMNS = ["height_m", "bmi", "sbp_dbp_ratio", "heart_rate_bmi_ratio"]


def map_binary_target(series: pd.Series) -> pd.Series:
    mapping = {"yes": 1, "y": 1, "true": 1, "1": 1, "no": 0, "n": 0, "false": 0, "0": 0}
    values = series.astype(str).str.strip().str.lower().replace(mapping)
    return pd.to_numeric(values, errors="coerce").astype("Int64")


def create_engineered_features(data: pd.DataFrame) -> pd.DataFrame:
    result = data.copy()
    result["height_m"] = result["Height (cm)"] / 100.0
    result["bmi"] = result["Weight (kg)"] / result["height_m"] ** 2
    result["sbp_dbp_ratio"] = result["Systolic blood pressure (mmHg)"] / result["Diastolic blood pressure (mmHg)"]
    result["heart_rate_bmi_ratio"] = result["Heart rate (bpm)"] / result["bmi"]
    return result


def prepare_xy(data: pd.DataFrame):
    engineered = create_engineered_features(data)
    target = map_binary_target(engineered[TARGET_COLUMN])
    features = engineered.drop(columns=[TARGET_COLUMN])
    valid = target.notna()
    return features.loc[valid].copy(), target.loc[valid].astype(int).copy()


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    numeric = features.select_dtypes(include=[np.number]).columns.tolist()
    categorical = features.select_dtypes(exclude=[np.number]).columns.tolist()
    transformers = []
    if numeric:
        transformers.append(("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric))
    if categorical:
        try:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        except TypeError:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
        transformers.append(("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", encoder),
        ]), categorical))
    return ColumnTransformer(transformers, remainder="drop")
