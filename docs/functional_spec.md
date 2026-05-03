# Functional Specification

This document describes planned behavior. The current repository contains TODO-only source placeholders, not implemented application logic.

## Data Science Pipeline

- Load raw CIDRZ MDR-TB data.
- Clean and standardize clinical fields.
- Engineer clinically meaningful features.
- Train baseline and candidate models.
- Evaluate models using classification metrics and clinically relevant error analysis.
- Save the selected model artifact.

## Planned Prediction API

- `GET /health` should return service status.
- `POST /predict` should accept one patient's clinical data.
- `POST /predict` should return:
  - Predicted treatment outcome.
  - Poor-outcome risk score.
  - Risk level: `LOW`, `MEDIUM`, or `HIGH`.
  - Class probabilities.
  - Patient-level feature explanation when SHAP artifacts are available.

## Planned Clinician UI

- Provide a clear form for patient data entry.
- Display prediction results without requiring statistical interpretation.
- Highlight risk level visibly.
- Show the top factors contributing to the prediction.
- Avoid storing patient data locally unless explicitly designed and approved.

## Audit And Storage

Prediction storage is optional in the first version. If enabled later, stored records must include consent, access control, audit logging, and retention rules.
