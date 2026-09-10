# SWIFT: Student Wellness Depression-Risk Estimation

This repository constitutes the reproducibility package for the SWIFT study and the associated manuscript prototype. It contains the training pipeline, validation workflows, calibration and explainability analyses, and a local full-stack application for inference and decision support in a publication-ready format.

## Appendix: Reproducibility and execution summary

The source code in this repository is organized to support complete replication of the study and transparent verification of the manuscript claims. The analytical workflows are implemented in `src/`, the primary model-training entry point is `scripts/run_pipeline.py`, and the prototype application is provided in `clinical_screening_app/`.

## Requirements

Python 3.10 or newer is required. Install the project dependencies as follows:

```text
pip install -r requirements.txt
```

## Dataset

The student-level analysis dataset is not redistributed in this repository because access is restricted by institutional privacy requirements. To reproduce the study, obtain the authorized dataset and place it at:

```text
data/database_majorproj.csv
```

The dataset must include the target variable `Depressive symptoms` and all features required by the preprocessing and feature-engineering pipeline defined in `src/feature_engineering.py`.

## Primary reproduction workflow

Run the primary training workflow from the repository root:

```text
python scripts/run_pipeline.py
```

This executes the study pipeline and saves the trained model and metadata to the project `artifacts/` directory for subsequent validation and deployment workflows.

### Additional analysis workflows

The scripts in `src/` support model comparison, calibration assessment, and explainability analyses, including:

- `benchmark.py` compares tree-based models.
- `calibration.py` generates a reliability diagram.
- `explainability.py` calculates SHAP-based feature importance when SHAP is installed.
- `publication_grade_clinical_ai_pipeline.py` reproduces the manuscript analysis workflow.
- `swift_corrected_validation.py` and `swift_balanced_validation.py` run corrected validation analyses.

Generated figures, metrics, and result tables are written to ignored output directories that are not committed to source control.

## Manuscript prototype

The local prototype used to operationalize the trained classifier is included in `clinical_screening_app/`. It is a full-stack application comprising a FastAPI backend and a React/Vite frontend for clinical screening inference, explanation summaries, and counterfactual recommendations within the manuscript demonstration setting.

### Launch the prototype from the repository root

Use the bundled Windows launcher, if available in the local environment:

```text
clinical_screening_app\START_SPIT_SWIFT.bat
```

Alternatively, launch the services explicitly:

```text
python clinical_screening_app/scripts/export_model.py
cd clinical_screening_app/backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

In a second terminal:

```text
cd clinical_screening_app/frontend
npm install
npm run dev
```

The frontend is served at `http://localhost:5173` and proxies inference requests to `http://localhost:8000`.

## Reproducibility checklist

1. Install Python 3.10+ and the repository dependencies:
   ```text
   pip install -r requirements.txt
   ```
2. Place the authorized dataset at `data/database_majorproj.csv`.
3. Confirm the dataset contains the target column `Depressive symptoms` and all required features.
4. Run the primary pipeline:
   ```text
   python scripts/run_pipeline.py
   ```
5. Optionally run the validation and benchmarking scripts in `src/`.
6. Export the prototype model and launch the local interface from `clinical_screening_app/`.
7. Verify produced outputs in `artifacts/` and any ignored result folders.

## Scope and availability

This repository contains the analysis source, reproducibility instructions, and the local prototype implementation described in the manuscript. It does not include private data, user records, virtual environments, or temporary intermediate files. No final publication notebook is included in the source project, and all computational materials are intended for reproducible research use only and for transparent methodological review.

## Code availability statement

The code is provided for research reproducibility and transparent methodological review. It is not a clinical diagnostic tool, and model outputs should be interpreted only within the appropriate professional, ethical, and institutional context.