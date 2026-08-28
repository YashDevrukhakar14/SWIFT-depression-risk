# SWIFT: Student Wellness Depression-Risk Estimation

This repository contains the reproducibility code for the SWIFT machine-learning study. It includes preprocessing, feature engineering, model development, validation, calibration, benchmarking, and explainability utilities.

## Requirements

Use Python 3.10 or newer and install the pinned dependencies:

```text
pip install -r requirements.txt
```

## Dataset

The original student-level dataset is not redistributed here because access is subject to applicable privacy and institutional restrictions. Obtain an authorized copy and place it at:

```text
data/database_majorproj.csv
```

The dataset must contain the target column `Depressive symptoms` and the feature columns used by `src/feature_engineering.py`.

## Reproduction

Run the primary training workflow from the repository root:

```text
python scripts/run_pipeline.py
```

Additional workflows are available in `src/`:

- `benchmark.py` compares tree-based models.
- `calibration.py` generates a reliability diagram.
- `explainability.py` calculates SHAP-based feature importance when SHAP is installed.
- `publication_grade_clinical_ai_pipeline.py` runs the publication analysis.
- `swift_corrected_validation.py` and `swift_balanced_validation.py` run corrected validation analyses.

Generated models, figures, and result tables are written to ignored output directories. The publication analysis requires the authorized dataset and may require additional optional packages listed in `requirements.txt`.

## Scope

This deposit contains analysis source and reproducibility instructions only. It does not include private data, serialized model binaries, user records, virtual environments, temporary files, or a publication notebook because no final notebook is present in the source project.

## Code Availability

The code is provided for research reproducibility. It is not a clinical diagnostic tool, and model outputs require appropriate professional and ethical review before interpretation.