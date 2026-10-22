# Clinical EHR Screening Application

This local full-stack dashboard implements the manuscript prototype for the SWIFT multi-domain passive EHR screening model. It provides an interactive clinical interface for inference, explanation summaries, and counterfactual risk-reduction recommendations within a transparent research workflow.

## Reproducibility workflow

### 1. Refresh the packaged model artifacts

```bash
python clinical_screening_app/scripts/export_model.py
```

This retrains the reference pipeline from the study dataset and exports the serialized model and metadata used by the application runtime for manuscript-level reproducibility.

### 2. Start the backend API

```bash
cd clinical_screening_app/backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Start the frontend interface

```bash
cd clinical_screening_app/frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite development server proxies `/api` requests to the backend service running on `http://localhost:8000`.

## API specification

**POST** `/api/predict_clinical`

The endpoint accepts demographic, cognitive, lifestyle, and vital-sign inputs; computes the engineered clinical features (including BMI, blood-pressure ratio, and heart-rate-to-BMI ratio); and returns the predicted probability, risk zone, model explanations, and bundled counterfactual interventions.

## System components

- `backend/` — FastAPI service for inference, feature engineering, coefficient-based explanations, and counterfactual suggestions
- `frontend/` — React + Vite clinical interface for user-facing screening and reporting
- `artifacts/` — Serialized trained pipeline and metadata used in deployment
- `scripts/export_model.py` — Reference export workflow for regenerating the app’s packaged model artifacts

## Validation note

The prototype is intended to reproduce the manuscript’s operational workflow in a local environment and to support transparent inspection of model behavior. It is a research-facing interface rather than a clinical decision system.
