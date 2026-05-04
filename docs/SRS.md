# Software Requirements Specification

## Purpose

The MDR-TB Treatment Outcomes Predictor is a clinical decision-support prototype that estimates a patient's risk of poor MDR-TB treatment outcomes and explains the main factors influencing the prediction.

## Scope

The system will support data preparation, model training, model evaluation, prediction serving, and a future clinician-facing interface. It is intended for research, validation, and controlled pilot use before any real clinical deployment.

Current repository status: working academic prototype. Source files include a Streamlit frontend, FastAPI backend, trained outcome-model service, and tests. The model is trained on the reconstructed project dataset and is not clinically validated.

## Users

- Clinicians reviewing MDR-TB patients.
- Data scientists training and validating models.
- System administrators deploying and monitoring the tool.

## Clinical Outcomes

Initial target outcomes:

- Treatment success.
- Death.
- Loss to follow-up.

Additional outcomes such as treatment failure may be added if the dataset and clinical team support them.

## System Context

```text
Clinician -> UI App -> FastAPI Backend -> ML Model + SHAP -> Prediction + Explanation
```

## Constraints

- Patient data must be protected and handled according to relevant ethical, institutional, and legal requirements.
- Model outputs must be explainable enough for clinical review.
- The system must not be used for patient care until clinically validated.
