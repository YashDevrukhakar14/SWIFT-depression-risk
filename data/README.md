# Dataset Provenance and Access Instructions

## Primary Source Citation
The data used in this study originate from a prospective cohort health assessment of French undergraduate university students:

> **Tran, A., Tran-Ba-Huy, P., Romero, A., Pourcher, T., & Rampal, P. (2017).**  
> *Health assessment in a large cohort of French university students: study design, participant characteristics and preliminary results.*  
> **PLOS ONE**, 12(11), e0188187.  
> DOI: [10.1371/journal.pone.0188187](https://doi.org/10.1371/journal.pone.0188187)

## Public Repository Deposition (Dryad)
The anonymized tabular dataset is openly available from the Dryad Digital Repository under a Creative Commons Zero (CC0 1.0) Public Domain Dedication:

> **Tran, A., Tran-Ba-Huy, P., Romero, A., Pourcher, T., & Rampal, P. (2018).**  
> *Data from: Health assessment in a large cohort of French university students: study design, participant characteristics and preliminary results.*  
> **Dryad Digital Repository**, Dataset.  
> DOI: [10.5061/dryad.54qt7](https://doi.org/10.5061/dryad.54qt7)

## Study Cohort & Ethical Governance
- **Institution:** University of Nice Sophia-Antipolis (UNS), France.
- **Population:** $N = 4,184$ undergraduate students undergoing a compulsory preventive medical consultation between September 2012 and June 2013.
- **Ethics & Privacy Approval:** The original study was approved by the French National Commission on Informatics and Liberty (*Commission Nationale de l'Informatique et des Libertés*, CNIL Authorization #1653896).
- **Secondary Analysis Notice:** The present SWIFT study conducts a secondary, retrospective machine-learning analysis using this publicly available, fully anonymized dataset. No individual re-identification was attempted or is possible.

## Acquisition & Placement
To reproduce the experimental pipeline:
1. Download the data table directly from Dryad at [https://doi.org/10.5061/dryad.54qt7](https://doi.org/10.5061/dryad.54qt7).
2. Save the tabular file locally inside this directory as:
   ```text
   data/database_majorproj.csv
   ```
3. The dataset must retain the original 59 raw wellness variables and the target variable (`Depressive symptoms`).
