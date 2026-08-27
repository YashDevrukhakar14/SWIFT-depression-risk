import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from predictor import ClinicalPredictor


def test_risk_zone_and_bundle_counterfactuals():
    predictor = ClinicalPredictor()
    payload = {
        "gender": "female",
        "financial_difficulties": True,
        "satisfied_with_living_conditions": False,
        "learning_disabilities": True,
        "difficulty_memorizing_lessons": True,
        "field_of_study": "engineering",
        "unbalanced_meals": True,
        "irregular_rhythm_of_meals": True,
        "parental_home": True,
        "height_cm": 165,
        "weight_kg": 72,
        "systolic_blood_pressure_mmhg": 140,
        "diastolic_blood_pressure_mmhg": 90,
        "heart_rate_bpm": 88,
    }

    result = predictor.predict(payload)

    assert result["risk_zone"] in {"green", "yellow", "red"}
    assert result["risk_zone"] == "red" or result["risk_zone"] == "yellow"
    assert result["counterfactuals"]
    assert all("message" in cf for cf in result["counterfactuals"])
