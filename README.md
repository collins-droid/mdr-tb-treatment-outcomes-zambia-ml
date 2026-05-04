# MDR-TB Treatment Outcomes Predictor

This project is a clinical decision-support prototype for predicting treatment outcomes among patients with multidrug-resistant tuberculosis (MDR-TB) in Zambia. Using real-world clinical data from CIDRZ, the system will analyze demographic, clinical, and treatment-related factors to identify patients at high risk of poor outcomes such as death, treatment failure, or loss to follow-up.

The goal is not only to train a model, but to design a usable tool that can eventually return a prediction, a risk level, and an explanation clinicians can understand.

Current status: working academic prototype. The repository includes a FastAPI backend, a Streamlit frontend, trained outcome-model logic, preprocessing helpers, model artifacts, and smoke tests. The current model is trained on the project dataset reconstructed from published aggregate counts and must not be treated as clinically validated.

## Project Structure

```text
data/                 Raw, processed, and external datasets
notebooks/            EDA and experimental notebooks
src/                  Data science pipeline modules and model logic
api/                  FastAPI backend modules
frontend/             Streamlit clinician-facing prototype
models/               Saved model artifacts
tests/                Automated tests
docs/                 Lightweight SRS and specs
```

## Current Capabilities

- Predict prototype treatment outcome risk using the trained outcome model.
- Return a probability distribution, poor-outcome risk level, and explanation.
- Serve predictions through a FastAPI backend.
- Provide a Streamlit frontend for fast deployment and demos.
- Preview the reconstructed project dataset where the local generator is available.

## Run

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start the API:

```bash
uvicorn api.main:app --reload
```

Start the frontend:

```bash
streamlit run frontend/app.py
```

## Team Workflow

This project uses a protected-branch workflow:

- `main` is stable production-ready code.
- `staging` is for integrated testing before release.
- `feature/*` branches are for individual work streams.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/team_workflow.md](docs/team_workflow.md) for branch rules, team responsibilities, and ready-to-paste GitHub issues.

## Current Development Phase

- Improve the trained outcome model and compare candidate algorithms in the Colab workflow.
- Keep the reconstructed-data limitation clearly documented for academic review.
- Add clinical review before any pilot deployment.

## Important Clinical Note

This repository is currently a research and engineering prototype. It must not be used for real clinical decisions until the data pipeline, model performance, calibration, bias checks, clinical validation, security controls, and deployment process have been reviewed and approved by qualified clinical and governance stakeholders.
