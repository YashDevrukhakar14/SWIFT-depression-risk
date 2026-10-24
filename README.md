# SWIFT: Student Wellness Intelligence Framework for Triage
## Machine Learning Reproducibility Package

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23510057.svg)](https://doi.org/10.5281/zenodo.23510057)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue.svg)](https://www.python.org/)

This repository contains the complete computational reproducibility package for the study:  
**"SWIFT: An Explainable Machine Learning Framework for Student Wellness-Based Depression Risk Estimation"**.

It includes the data-preprocessing workflows, feature-engineering routines, 17-model comparative benchmark, primary Logistic Regression benchmark with 1,000-replication bootstrap confidence intervals, Optuna sensitivity analysis, calibration assessment, explainability (SHAP & LIME) pipelines, and the interactive research demonstration platform.

---

## Academic Research Scope and Non-Clinical Disclaimer
The SWIFT framework is an **educational research decision-support prototype** developed to evaluate the feasibility of transparent, explainable machine-learning methods for student wellness risk estimation. 

- **Not a Medical Device:** SWIFT is **not** a clinical diagnostic tool, medical screening instrument, or autonomous triage software.
- **Human Supervision Required:** All outputs constitute uncalibrated statistical risk indicators intended solely to assist authorized human counsellors and student wellness personnel within a supervised educational setting.
- **No Autonomous Decisions:** The framework does not prescribe interventions, make autonomous clinical determinations, or generate automated counterfactual clinical decisions.

---

## Dataset Provenance and Access
This study performs a secondary, retrospective analysis on a publicly available, fully anonymized health assessment cohort:
- **Original Source Publication:**  
  Tran, A., Tran-Ba-Huy, P., Romero, A., Pourcher, T., & Rampal, P. (2017). *Health assessment in a large cohort of French university students: study design, participant characteristics and preliminary results.* **PLOS ONE**, 12(11): e0188187. DOI: [10.1371/journal.pone.0188187](https://doi.org/10.1371/journal.pone.0188187).
- **Dryad Repository Deposition:**  
  Tran, A. et al. (2018). *Data from: Health assessment in a large cohort of French university students...* **Dryad Digital Repository**, Dataset. DOI: [10.5061/dryad.54qt7](https://doi.org/10.5061/dryad.54qt7).
- **Cohort Size:** $N = 4,184$ undergraduate students from the University of Nice Sophia-Antipolis (UNS), France (CNIL Ethics Approval #1653896).

### Placing the Dataset:
Download `database_majorproj.csv` from the Dryad link above and place it in the `data/` directory:
```text
data/database_majorproj.csv
```

---

## System Requirements
- **Operating System:** Platform-independent (tested on Windows 11, Ubuntu 22.04 LTS, macOS Sequoia).
- **Python Version:** Python 3.10 or 3.11 recommended.
- **Hardware:** Standard consumer CPU (minimum 8 GB RAM; no dedicated GPU required).

---

## Quickstart & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YashDevrukhakar14/SWIFT-depression-risk.git
   cd SWIFT-student-wellness
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install pinned dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Experimental Protocol & Configurations

To guarantee leakage-controlled evaluation, the experimental protocol strictly enforces the following design:

1. **Partitioning:**
   - Stratified train/test split (75% training, $N=3,138$; 25% held-out test, $N=1,046$; random seed `42`).
   - The test set contains 132 positive risk cases and 914 negative cases (prevalence: 12.62%).
   - All data-dependent preprocessors (imputation, scaling, one-hot encoding) are fitted strictly on the training partition and applied without modification to the test partition.

2. **Primary Benchmark Model:**
   - **Estimator:** Logistic Regression (`solver='lbfgs'`, `C=1.0`, `class_weight='balanced'`, `max_iter=5000`, `random_state=42`).
   - **Decision Threshold:** Pre-fixed at $\tau = 0.5$ (uncalibrated screening risk score).
   - **Uncertainty Quantification:** 1,000 non-parametric bootstrap replications on the held-out test set generating 95% percentile confidence intervals.

3. **17-Model Comparative Benchmark:**
   - Fixed-configuration comparison across linear, tree, boosting, ensemble, neural, and explainable paradigms under identical training/testing splits.
   - Probability metrics (Brier score) are reported strictly for models supporting native probability outputs; non-probabilistic models (e.g., Linear SVM, Ridge) are marked as `N/A`.

4. **Secondary Sensitivity Analysis (Optuna Hyperparameter Tuning):**
   - Hyperparameter exploration performed using **five-fold stratified cross-validation restricted entirely to the training partition** ($X_{\text{train}}$) using `TPESampler(seed=42)`.
   - Objective: maximize cross-validated ROC-AUC.
   - Evaluated once on the held-out test set to assess sensitivity relative to the fixed $C=1.0$ benchmark.

5. **Explainable AI (XAI) Methods:**
   - **Global Feature Attribution:** `shap.LinearExplainer` applied to the primary Logistic Regression model using background statistics derived from $X_{\text{train}}$, aggregated via mean absolute SHAP values ($\overline{|\phi|}$).
   - **Local Instance Explanations:** `lime.lime_tabular.LimeTabularExplainer` fitted on training reference distributions (5,000 sample perturbations, 10 features) explaining a representative test case closest to the median risk score.
   - **Transparent Log-Odds Decomposition:** Exact feature contributions ($\beta_j \cdot x_j$) displayed directly in the prototype dashboard.

---

## Reproducing Manuscript Results

A single unified script executes the entire empirical analysis and outputs verified metrics, tables, and figures:

```bash
python reproduce_results.py
```

### Execution Flow of `reproduce_results.py`:
1. **Data Preprocessing & Feature Engineering:** Validates raw input, constructs derived indicators, and applies stratified 75/25 train-test split.
2. **Primary Baseline Logistic Regression:** Trains $C=1.0$ balanced model and computes point estimates.
3. **1,000-Replication Bootstrap Confidence Intervals:** Computes percentile 95% CIs across all 11 performance metrics.
4. **17-Model Benchmark Evaluation:** Generates manuscript Table 5 (`publication_results/model_comparison.csv`).
5. **Optuna Sensitivity Analysis:** Runs 15-trial training-only 5-fold CV hyperparameter search and evaluates the resulting configuration.
6. **Calibration & Reliability Assessment:** Computes Brier score, calibration intercept, and slope; generates `calibration_reliability_diagram.png`.
7. **Explainability Pipeline:** Computes global SHAP importances and generates local LIME explanations.

Generated outputs are stored in `publication_results/`:
- `model_comparison.csv` (Table 5)
- `baseline_lr_metrics.csv` & `baseline_lr_bootstrap_ci.csv` (Table 6)
- `optuna_sensitivity_metrics.csv`
- `shap_global_importance.csv`
- `calibration_reliability_diagram.png`

---

## Interactive Prototype Platform

The repository also includes the local full-stack research prototype demonstrating the human-in-the-loop decision-support interface:

### Backend (FastAPI):
```bash
cd clinical_screening_app/backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend (React / Vite):
```bash
cd clinical_screening_app/frontend
npm install
npm run dev
```
Access the dashboard at `http://localhost:5173`.

---

## Repository Directory Structure

```text
SWIFT-student-wellness/
├── data/
│   ├── database_majorproj.csv       # Anonymized dataset from Dryad (user-placed)
│   └── README.md                    # Detailed provenance and Dryad attribution
├── src/
│   ├── feature_engineering.py       # Data cleaning and deterministic feature engineering
│   ├── publication_grade_pipeline.py# 17-model benchmark and evaluation functions
│   ├── explainability.py            # SHAP LinearExplainer and LIME routines
│   └── calibration.py               # Calibration curve and reliability diagram routines
├── scripts/
│   └── run_pipeline.py              # CLI entry point
├── publication_results/             # Verified empirical outputs and manuscript tables
│   ├── model_comparison.csv         # Table 5 benchmark comparison
│   ├── baseline_lr_bootstrap_ci.csv # 1,000-replication bootstrap 95% CIs
│   └── calibration_reliability.png  # Reliability plot
├── clinical_screening_app/          # Full-stack research prototype
│   ├── backend/                     # FastAPI inference service
│   └── frontend/                    # React / Vite dashboard
├── reproduce_results.py             # Single-entry master reproduction pipeline
├── requirements.txt                 # Pinned dependencies for Python 3.10/3.11
├── LICENSE                          # MIT open-source license
└── README.md                        # Master documentation
```

---

## Citation
If you use the SWIFT framework, code, or methodology in your research, please cite:

```bibtex
@article{swift2026depression,
  title={SWIFT: An Explainable Machine Learning Framework for Student Wellness-Based Depression Risk Estimation},
  author={Y. D. and P. K.},
  journal={Journal of Educational Data Mining / Health Informatics},
  year={2026},
  doi={10.5281/zenodo.22149139}
}
```

---

## License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
