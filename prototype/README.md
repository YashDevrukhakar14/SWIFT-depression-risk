# Clinical EHR Screening Application

Local full-stack dashboard for the Multi-Domain Passive EHR Screening Model (MDD).

## Quick Start

### 1. Export / refresh model artifacts (first run)

```bash
python clinical_screening_app/scripts/export_model.py
```

### 2. Backend (FastAPI)

```bash
cd clinical_screening_app/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend (React + Vite)

```bash
cd clinical_screening_app/frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the Vite dev server proxies `/api` to the backend.

## API

**POST** `/api/predict_clinical`

Accepts demographic, cognitive, lifestyle, and vitals fields; computes BMI, BP ratio, heart-rate/BMI ratio, and categorical bins before scoring with the peak Logistic Regression pipeline.

## Architecture

- `backend/` — FastAPI inference, feature engineering, coefficient-based explanations, counterfactual suggestions
- `frontend/` — Dense two-panel clinical UI (slate/navy theme)
- `artifacts/` — Serialized sklearn pipeline + metadata
- `scripts/export_model.py` — Retrain and export from `database_majorproj.csv`
