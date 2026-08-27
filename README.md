# SWIFT: Student Wellness Depression-Risk Estimation
This repository contains the computational framework and prototype code for the SWIFT model.

## Quickstart
1. Install dependencies: `pip install -r requirements.txt`
2. Run data processing & training: `python train.py`
3. Launch prototype UI: `streamlit run app.py`

Optional XAI evaluation: `python xai_evaluation.py`

## Study Source Layout
- `pipelines/` - publication-grade benchmarking, corrected validation, and bootstrap pipelines.
- `feature_engineering.py` - shared preprocessing and engineered wellness features.
- `prototype/backend/` - FastAPI prediction service, feature engineering, explanations, and tests.
- `prototype/frontend/` - React/Vite interactive web application prototype.
- `prototype/scripts/export_model.py` - exports the prototype model artifact.

### Full Web Prototype
1. Install backend dependencies: `pip install -r prototype/backend/requirements.txt`
2. Start the API: `cd prototype/backend` then `uvicorn main:app --reload --port 8000`
3. In another terminal, start the UI: `cd prototype/frontend`, `npm install`, then `npm run dev`
4. Open `http://localhost:5173`
