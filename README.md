# MDR-TB Treatment Outcomes Predictor

This project is a clinical decision-support prototype for predicting treatment outcomes among patients with multidrug-resistant tuberculosis (MDR-TB) in Zambia. Using real-world clinical data from CIDRZ, the system will analyze demographic, clinical, and treatment-related factors to identify patients at high risk of poor outcomes such as death, treatment failure, or loss to follow-up.

The goal is not only to train a model, but to design a usable tool that can eventually return a prediction, a risk level, and an explanation clinicians can understand.

Current status: documentation-first scaffold. The repository is intentionally using TODO placeholders and docstrings before implementation begins.

## Project Structure

```text
data/                 Raw, processed, and external datasets
notebooks/            EDA and experimental notebooks
src/                  Planned data science pipeline modules
api/                  Planned FastAPI backend modules
frontend/             Placeholder for the clinician-facing UI
models/               Saved model artifacts
tests/                Automated tests
docs/                 Lightweight SRS and specs
```

## Planned Capabilities

- Predict treatment outcome: success, death, or loss to follow-up.
- Return a probability distribution and risk level.
- Explain patient-level risk factors using SHAP.
- Serve predictions through a FastAPI backend.
- Support a future web or mobile frontend for clinic use.

## Team Workflow

This project uses a protected-branch workflow:

- `main` is stable production-ready code.
- `staging` is for integrated testing before release.
- `feature/*` branches are for individual work streams.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/team_workflow.md](docs/team_workflow.md) for branch rules, team responsibilities, and ready-to-paste GitHub issues.

## Current Development Phase

- Finalize SRS, functional specification, and non-functional specification.
- Confirm team ownership and Git workflow.
- Define data dictionary and target outcome labels.
- Decide which modules should be implemented first.
- Only add executable code after the relevant issue and design notes are approved.

## Important Clinical Note

This repository is currently a research and engineering scaffold. It must not be used for real clinical decisions until the data pipeline, model performance, calibration, bias checks, clinical validation, security controls, and deployment process have been reviewed and approved by qualified clinical and governance stakeholders.
