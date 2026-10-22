"""Clinical prediction engine with explainability and counterfactual guidance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

try:
    from .feature_engineering import _yes_no, compute_engineered_features
except ImportError:
    from feature_engineering import _yes_no, compute_engineered_features

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"

YN_BOOL_FIELDS = {
    "financial_difficulties", "satisfied_with_living_conditions",
    "learning_disabilities", "difficulty_memorizing_lessons",
    "unbalanced_meals", "irregular_rhythm_of_meals", "parental_home",
    "professional_objective", "living_with_partner_child",
    "having_only_one_parent", "siblings", "long_commute",
    "additional_income", "cmu", "eating_junk_food", "on_a_diet",
    "urinalysis_glycosuria", "urinalysis_proteinuria", "urinalysis_hematuria",
    "urinalysis_leukocyturia", "urinalysis_nitrite", "abnormal_urinalysis",
    "binge_drinking", "marijuana_use", "other_recreational_drugs",
    "anxiety_symptoms", "panic_attack_symptoms",
}

# Maps API field names → CSV column names
COLUMN_MAP = {
    "gender":                           "Gender",
    "age":                              "Age (4 levels)",
    "field_of_study":                   "Field of study",
    "year_of_university":               "Year of university",
    "learning_disabilities":            "Learning disabilities",
    "difficulty_memorizing_lessons":    "Difficulty memorizing lessons",
    "professional_objective":           "Professional objective",
    "satisfied_with_living_conditions": "Satisfied with living conditions",
    "living_with_partner_child":        "Living with a partner/child",
    "parental_home":                    "Parental home",
    "having_only_one_parent":           "Having only one parent",
    "siblings":                         "Siblings",
    "long_commute":                     "Long commute",
    "mode_of_transportation":           "Mode of transportation",
    "financial_difficulties":           "Financial difficulties",
    "additional_income":                "Additional income",
    "cmu":                              "C.M.U.",
    "irregular_rhythm_of_meals":        "Irregular rhythm of meals",
    "unbalanced_meals":                 "Unbalanced meals",
    "eating_junk_food":                 "Eating junk food",
    "on_a_diet":                        "On a diet",
    "physical_activity_3":              "Physical activity(3 levels)",
    "physical_activity_2":              "Physical activity(2 levels)",
    "weight_kg":                        "Weight (kg)",
    "height_cm":                        "Height (cm)",
    "heart_rate_bpm":                   "Heart rate (bpm)",
    "urinalysis_glycosuria":            "Urinalysis (glycosuria)",
    "urinalysis_proteinuria":           "Urinalysis (proteinuria)",
    "urinalysis_hematuria":             "Urinalysis (hematuria)",
    "urinalysis_leukocyturia":          "Urinalysis leukocyturia)",
    "urinalysis_nitrite":               "Urinalysis (positive nitrite test)",
    "abnormal_urinalysis":              "Abnormal urinalysis",
    "cigarette_smoker_5":               "Cigarette smoker (5 levels)",
    "cigarette_smoker_3":               "Cigarette smoker (3 levels)",
    "drinker_3":                        "Drinker (3 levels)",
    "drinker_2":                        "Drinker (2 levels)",
    "binge_drinking":                   "Binge drinking",
    "marijuana_use":                    "Marijuana use",
    "other_recreational_drugs":         "Other recreational drugs",
    "anxiety_symptoms":                 "Anxiety symptoms",
    "panic_attack_symptoms":            "Panic attack symptoms",
    "systolic_blood_pressure_mmhg":     "Systolic blood pressure (mmHg)",
    "diastolic_blood_pressure_mmhg":    "Diastolic blood pressure (mmHg)",
}


class ClinicalPredictor:
    def __init__(self):
        self.pipeline: Pipeline = joblib.load(ARTIFACTS_DIR / "clinical_model.joblib")
        with open(ARTIFACTS_DIR / "model_metadata.json", encoding="utf-8") as f:
            self.metadata = json.load(f)
        self.threshold = float(self.metadata["decision_threshold"])
        self.risk_threshold_percent = float(
            self.metadata.get("risk_threshold_percent", self.threshold * 100.0)
        )
        self.feature_columns = self.metadata["feature_columns"]
        self.defaults = self.metadata["defaults"]

    def _payload_to_row(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = dict(self.defaults)
        for api_key, csv_col in COLUMN_MAP.items():
            if api_key not in payload:
                continue
            value = payload[api_key]
            if api_key in YN_BOOL_FIELDS:
                row[csv_col] = _yes_no(value)
            elif api_key == "gender":
                row[csv_col] = str(value).strip().lower()
            else:
                row[csv_col] = value

        # Derive "Irregular rhythm or unbalanced meals" from its components
        irr = row.get("Irregular rhythm of meals", "no")
        unb = row.get("Unbalanced meals", "no")
        row["Irregular rhythm or unbalanced meals"] = (
            "yes" if irr == "yes" or unb == "yes" else "no"
        )

        engineered = compute_engineered_features({
            "Height (cm)":                    row.get("Height (cm)"),
            "Weight (kg)":                    row.get("Weight (kg)"),
            "Systolic blood pressure (mmHg)": row.get("Systolic blood pressure (mmHg)"),
            "Diastolic blood pressure (mmHg)": row.get("Diastolic blood pressure (mmHg)"),
            "Heart rate (bpm)":               row.get("Heart rate (bpm)"),
        })
        row.update(engineered)
        return row

    def _to_dataframe(self, row: dict[str, Any]) -> pd.DataFrame:
        data = {col: row.get(col, self.defaults.get(col)) for col in self.feature_columns}
        return pd.DataFrame([data])

    def _transformed_vector(self, X: pd.DataFrame):
        preprocess = self.pipeline.named_steps["preprocess"]
        model = self.pipeline.named_steps["model"]
        Xt = preprocess.transform(X)
        try:
            names = preprocess.get_feature_names_out().tolist()
        except Exception:
            names = [f"feature_{i}" for i in range(Xt.shape[1])]
        return Xt, names, model

    def predict(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self._payload_to_row(payload)
        X = self._to_dataframe(row)
        probability = float(self.pipeline.predict_proba(X)[0, 1])
        high_risk = probability >= self.threshold
        risk_percent = round(probability * 100, 1)
        risk_zone, risk_zone_label, risk_zone_description = self._risk_zone(risk_percent)

        Xt, names, model = self._transformed_vector(X)
        coef = model.coef_[0]
        intercept = float(model.intercept_[0])
        contributions = coef * Xt[0]

        explanation = []
        for name, contrib, val in zip(names, contributions, Xt[0]):
            explanation.append({
                "feature": self._display_name(name),
                "contribution": float(contrib),
                "direction": "positive" if contrib >= 0 else "negative",
                "transformed_value": float(val),
            })
        explanation.sort(key=lambda x: abs(x["contribution"]), reverse=True)

        counterfactuals = self._counterfactuals(payload, probability)

        return {
            "probability": round(probability, 4),
            "probability_percent": risk_percent,
            "decision_threshold": self.threshold,
            "risk_threshold_percent": self.risk_threshold_percent,
            "high_risk": high_risk,
            "risk_zone": risk_zone,
            "risk_zone_label": risk_zone_label,
            "risk_zone_description": risk_zone_description,
            "clinical_status": (
                "High Clinical Probability of Active Depressive Symptoms"
                if high_risk else
                "Low Clinical Probability of Active Depressive Symptoms"
            ),
            "risk_label": "ELEVATED SYSTEMIC RISK" if high_risk else "LOW PROTOCOL RISK",
            "engineered_features": {
                "bmi": round(row.get("bmi", 0) or 0, 2),
                "sbp_dbp_ratio": round(row.get("sbp_dbp_ratio", 0) or 0, 3),
                "heart_rate_bmi_ratio": round(row.get("heart_rate_bmi_ratio", 0) or 0, 3),
                "bmi_cat": row.get("bmi_cat"),
                "bp_cat": row.get("bp_cat"),
            },
            "calibration_metrics": {
                "roc_auc": self.metadata["roc_auc"],
                "mcc": self.metadata["mcc"],
                "brier_score": self.metadata["brier_score"],
            },
            "explanation": explanation[:12],
            "logit_intercept": intercept,
            "logit_feature_shift": float(np.sum(contributions)),
            "counterfactuals": counterfactuals,
        }

    def _risk_zone(self, pct: float):
        if pct < 45.0:
            return "green", "Green Zone", "Routine ambient screening with watchful monitoring."
        if pct < self.risk_threshold_percent:
            return "yellow", "Yellow Zone", "Sub-clinical watchlist: monitor lifestyle and wellbeing factors closely."
        return "red", "Red Zone", "Active clinical referral required for follow-up assessment."

    def _display_name(self, name: str) -> str:
        n = name.replace("num__", "").replace("cat__", "").replace("_", " ")
        replacements = {
            "Difficulty memorizing lessons yes": "Difficulty Memorizing = Yes",
            "Financial difficulties yes": "Financial Difficulties = Yes",
            "Learning disabilities yes": "Learning Disabilities = Yes",
            "Unbalanced meals yes": "Unbalanced Meals = Yes",
            "Irregular rhythm of meals yes": "Irregular Meal Rhythm = Yes",
            "Parental home yes": "Parental Home = Yes",
            "Gender female": "Female Gender",
            "Gender male": "Male Gender",
            "Anxiety symptoms yes": "Anxiety Symptoms = Yes",
            "Panic attack symptoms yes": "Panic Attacks = Yes",
            "Binge drinking yes": "Binge Drinking = Yes",
            "Marijuana use yes": "Marijuana Use = Yes",
        }
        for key, label in replacements.items():
            if key.lower() in n.lower():
                return label
        return n.title()

    def _counterfactuals(self, payload: dict[str, Any], base_prob: float):
        if base_prob < self.threshold:
            return [{"message": "Profile remains within safe protocol bounds at current inputs.", "probability_delta_percent": 0.0}]

        bundles = [
            {
                "name": "Lifestyle Domain",
                "description": "Regularize meals and improve living satisfaction",
                "changes": [
                    ("unbalanced_meals", False), ("irregular_rhythm_of_meals", False),
                    ("satisfied_with_living_conditions", True),
                ],
            },
            {
                "name": "Stress Domain",
                "description": "Reduce financial strain and address cognitive burden",
                "changes": [
                    ("financial_difficulties", False), ("difficulty_memorizing_lessons", False),
                    ("learning_disabilities", False),
                ],
            },
            {
                "name": "Substance Reduction Domain",
                "description": "Eliminate substance use risk factors",
                "changes": [
                    ("binge_drinking", False), ("marijuana_use", False),
                    ("cigarette_smoker_5", "no"),
                ],
            },
        ]

        suggestions = []
        for bundle in bundles:
            trial = dict(payload)
            applied = []
            for field, target in bundle["changes"]:
                if field not in payload:
                    continue
                curr = payload[field]
                if isinstance(curr, bool) and curr != target:
                    trial[field] = target
                    applied.append((field, target))
                elif isinstance(curr, str) and curr != target:
                    trial[field] = target
                    applied.append((field, target))
            if not applied:
                continue
            new_prob = float(self.predict_proba_only(trial))
            delta = (base_prob - new_prob) * 100
            if delta > 0.1:
                change_summary = ", ".join(
                    f"{f.replace('_', ' ')} → {'Yes' if t is True else 'No' if t is False else t}"
                    for f, t in applied
                )
                suggestions.append({
                    "intervention": bundle["name"],
                    "field": bundle["description"],
                    "target_value": True,
                    "new_probability": round(new_prob, 4),
                    "probability_delta_percent": round(delta, 1),
                    "message": f"{bundle['name']} ({change_summary}) reduces risk by {delta:.1f} percentage points.",
                })

        suggestions.sort(key=lambda x: x["probability_delta_percent"], reverse=True)
        if not suggestions:
            return [{"message": "No bundled domain change produced a measurable probability shift.", "probability_delta_percent": 0.0}]
        return suggestions[:3]

    def predict_proba_only(self, payload: dict[str, Any]) -> float:
        row = self._payload_to_row(payload)
        X = self._to_dataframe(row)
        return float(self.pipeline.predict_proba(X)[0, 1])
