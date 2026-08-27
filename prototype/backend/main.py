"""FastAPI backend for SPIT SWIFT — Multi-Domain Passive EHR Screening."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

try:
    from .predictor import ClinicalPredictor
except ImportError:
    from predictor import ClinicalPredictor

app = FastAPI(
    title="SPIT SWIFT — Clinical EHR Screening Engine",
    description="Multi-Domain Passive EHR Screening Model for Major Depressive Disorder",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = ClinicalPredictor()
USERS_FILE = Path(__file__).parent / "users.json"


# ─── Auth helpers ───────────────────────────────────────────────
def _load_users() -> list:
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE, encoding="utf-8") as f:
        return json.load(f).get("users", [])


def _save_users(users: list) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({"users": users}, f, indent=2)


def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ─── Auth schemas ───────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ─── Clinical input schema (all dataset features) ───────────────
class ClinicalInput(BaseModel):
    # Demographics
    gender: str = Field(default="female")
    age: str = Field(default="20 and more")
    field_of_study: str = Field(default="medicine and allied programs")
    year_of_university: str = Field(default="first")
    # Cognitive
    learning_disabilities: bool = False
    difficulty_memorizing_lessons: bool = False
    professional_objective: bool = True
    # Social / Housing
    satisfied_with_living_conditions: bool = True
    living_with_partner_child: bool = False
    parental_home: bool = True
    having_only_one_parent: bool = False
    siblings: bool = True
    long_commute: bool = False
    mode_of_transportation: str = Field(default="by public transportation")
    # Financial
    financial_difficulties: bool = False
    additional_income: bool = False
    cmu: bool = False
    # Dietary / Lifestyle
    irregular_rhythm_of_meals: bool = False
    unbalanced_meals: bool = False
    eating_junk_food: bool = False
    on_a_diet: bool = False
    physical_activity_3: str = Field(default="no")
    physical_activity_2: str = Field(default="no activity or occasionally")
    # Vitals
    height_cm: float = Field(default=169.0, gt=0)
    weight_kg: float = Field(default=62.0, gt=0)
    systolic_blood_pressure_mmhg: float = Field(default=120.0, gt=0)
    diastolic_blood_pressure_mmhg: float = Field(default=80.0, gt=0)
    heart_rate_bpm: float = Field(default=73.0, gt=0)
    # Urinalysis
    urinalysis_glycosuria: bool = False
    urinalysis_proteinuria: bool = False
    urinalysis_hematuria: bool = False
    urinalysis_leukocyturia: bool = False
    urinalysis_nitrite: bool = False
    abnormal_urinalysis: bool = False
    # Substance use
    cigarette_smoker_5: str = Field(default="no")
    cigarette_smoker_3: str = Field(default="no")
    drinker_3: str = Field(default="no")
    drinker_2: str = Field(default="no or occasionally")
    binge_drinking: bool = False
    marijuana_use: bool = False
    other_recreational_drugs: bool = False
    # Mental health indicators
    anxiety_symptoms: bool = False
    panic_attack_symptoms: bool = False


# ─── Auth endpoints ─────────────────────────────────────────────
@app.post("/api/signup")
def signup(req: SignupRequest):
    users = _load_users()
    if any(u["username"].lower() == req.username.lower() for u in users):
        raise HTTPException(status_code=400, detail="Username already exists.")
    if any(u["email"].lower() == req.email.lower() for u in users):
        raise HTTPException(status_code=400, detail="Email already registered.")
    users.append({
        "name": req.name,
        "username": req.username,
        "email": req.email,
        "password_hash": _hash_password(req.password),
    })
    _save_users(users)
    return {"message": "Account created successfully.", "username": req.username, "name": req.name}


@app.post("/api/login")
def login(req: LoginRequest):
    users = _load_users()
    user = next((u for u in users if u["username"].lower() == req.username.lower()), None)
    if not user or user["password_hash"] != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {"message": "Login successful.", "username": user["username"], "name": user["name"]}


# ─── Health check ───────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "model": predictor.metadata["model_name"]}


# ─── Prediction endpoint ────────────────────────────────────────
@app.post("/api/predict_clinical")
async def predict_clinical(payload: ClinicalInput):
    await asyncio.sleep(0.85)
    result = predictor.predict(payload.model_dump())
    return result


@app.get("/api/schema")
def schema():
    return {
        "input_fields": list(ClinicalInput.model_json_schema()["properties"].keys()),
        "decision_threshold": predictor.threshold,
        "calibration_metrics": predictor.metadata,
    }
