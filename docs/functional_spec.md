# Functional Specification

This document describes implemented prototype behavior and the intended direction for later validated model work.

## Data Science Pipeline

- Load raw CIDRZ MDR-TB data.
- Clean and standardize clinical fields.
- Engineer clinically meaningful features.
- Train the current outcome model and candidate models.
- Evaluate models using classification metrics and clinically relevant error analysis.
- Save the selected model artifact.

## Prediction API

- `GET /health` returns service status.
- `POST /predict` accepts one patient's clinical data.
- `POST /predict` returns:
  - Predicted treatment outcome.
  - Poor-outcome risk score.
  - Risk level: `LOW`, `MEDIUM`, or `HIGH`.
  - Class probabilities.
  - Patient-level feature explanation when SHAP artifacts are available.

## Clinician UI

- Provides a clear Streamlit form for patient data entry.
- Displays prediction results without requiring statistical interpretation.
- Highlights risk level visibly.
- Shows the top factors contributing to the prediction.
- Avoids storing patient data locally.

## Audit And Storage

Prediction storage is optional in the first version. If enabled later, stored records must include consent, access control, audit logging, and retention rules.
