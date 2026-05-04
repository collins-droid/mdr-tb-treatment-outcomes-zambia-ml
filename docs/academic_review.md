# Academic Review Notes

## Current Strengths

- The repository now has an end-to-end implementation: data preparation, model training, saved artifact, FastAPI prediction service, Streamlit frontend, and tests.
- The training pipeline is reproducible through `python -m src.models.train`.
- The API exposes a consistent prediction contract with predicted outcome, probabilities, risk level, and feature-level explanation.
- The frontend follows the SRS more closely by presenting a patient assessment workflow instead of a loose dashboard.

## Methodological Risk

The current dataset is reconstructed from published aggregate counts. That is acceptable for an academic software prototype if the limitation is declared clearly. It is not equivalent to independently collected patient-level clinical data.

Key implications:

- Row-level relationships between predictors may be artificial because the paper does not publish every joint distribution.
- Reported performance is internal performance on reconstructed records, not evidence of clinical generalization.
- The model can demonstrate software competence and ML workflow competence, but it cannot validate the original paper's conclusions.
- Any wording such as "clinically validated", "real-world deployed model", or "patient-ready decision support" should be avoided.

## Academic Positioning

Use this framing:

> This project implements and evaluates an end-to-end MDR-TB treatment outcome prediction prototype using a reconstructed project dataset derived from published aggregate statistics. The purpose is to demonstrate data engineering, model development, API integration, explainable prediction output, and frontend deployment. Clinical deployment would require independent patient-level data, external validation, calibration, bias assessment, and governance approval.

## Recommended Colab Contents

The Colab notebook should include:

- Project title and research objective.
- Dataset generation/loading.
- Dataset description and source paper citation.
- Clear data validity statement.
- Exploratory data analysis.
- Target definition.
- Train/test split.
- Model training.
- Evaluation metrics and confusion matrix.
- Feature interpretation.
- Saved artifact export.
- Limitations and future work.
