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
- Preview model performance metrics (F1, ROC-AUC) and diagnostic curves.
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

## Clinical Signal Verification (Audit)

We performed a formal clinical signal audit by comparing our reconstructed mock dataset against the original findings reported in the **Chanda (2024)** research paper.

- **Structural Accuracy**: The dataset perfectly matches the paper's aggregate counts (N=183, Mean Age=35.2, 21.3% Mortality).
- **Signal Discovery**: Our audit revealed that while the totals are correct, most clinical signals (like the HIV-mortality link) were lost during reconstruction due to randomized shuffling.
- **Model Limitation**: Currently, the model is primarily learning from **Gender** and **Age Group** signals, as these were the only variables explicitly constrained to match the original research findings.

For the full statistical audit and p-value comparison, see [docs/findings.md](docs/findings.md).

## Model Findings & Fixes

### v1 Issues (Logistic Regression baseline)
- **Overconfident Mortality Prediction:** The model originally predicted disproportionately high probabilities for "Died" due to `class_weight="balanced"` in `LogisticRegression`. Removing it improved accuracy from ~34.7% to 60.8%.
- **Year of Diagnosis:** Removed as a vestigial UI input — it was never in the model feature set.

### v2 Fixes (Random Forest — Calibrated)
Following a formal **Model Alignment Audit** against Chanda (2024)'s adjusted regression table, three critical issues were identified and resolved:

| Issue | Root Cause | Fix Applied |
| :--- | :--- | :--- |
| **~65% death predictions** far above the paper's 21.3% overall mortality | RF unconstrained on 183 rows — memorising training noise | `max_depth=4`, `min_samples_leaf=5`, `CalibratedClassifierCV (isotonic)` |
| **Kabwe over-amplified** as a mortality driver | District included as a feature despite aOR=0.544, **p=0.401** (non-sig) in paper | **Removed `district` from training features** |
| **No systematic hyperparameter search** | All RF parameters were defaults | `GridSearchCV` over `{max_depth, min_samples_leaf, n_estimators}` using stratified 5-fold CV |

The updated model is versioned as **`randomforest-calibrated-v2`** and retrains automatically on Streamlit Cloud deployment.

For the full alignment audit and evidence, see [docs/findings.md](docs/findings.md).

## Important Clinical Note

This repository is currently a research and engineering prototype. It must not be used for real clinical decisions until the data pipeline, model performance, calibration, bias checks, clinical validation, security controls, and deployment process have been reviewed and approved by qualified clinical and governance stakeholders.
