# Team Workflow

## Branches

```text
main        stable production branch
staging     integration branch for testing
feature/*   individual work branches
```

Examples:

```text
feature/data-preprocessing
feature/model-training
feature/api-backend
feature/frontend-ui
feature/shap-explainability
```

## Release Flow

```text
feature/* -> pull request -> staging -> test -> pull request -> main
```

Nobody should push directly to `main` or `staging`.

## Migrating From `feature` To `feature/*`

A single branch named `feature` blocks branches like `feature/model-training`. Before creating `feature/*` branches, confirm whether the old `feature` branch contains useful work.

If it is obsolete:

```bash
git branch -d feature
git push origin --delete feature
```

If it must be kept:

```bash
git branch -m feature feature/legacy
git push origin feature/legacy
git push origin --delete feature
```

## Board Columns

- Todo
- In Progress
- Review
- Done

## Issue Format

Each issue should include:

```text
Assigned to: [Name]
Branch: feature/[workstream]
Definition of done:
- [ ] Testable output exists
- [ ] Documentation or notes updated
- [ ] Reviewer can verify the change
```

## Division Of Labour

### Data / ML Engineer

Branch: `feature/model-training`

Owns:

- Data cleaning.
- Feature engineering.
- Model training.
- Model evaluation.
- Model artifact export.

Issues:

- [ ] Load and explore CIDRZ dataset.
- [ ] Handle missing values.
- [ ] Encode categorical variables.
- [ ] Train Logistic Regression outcome model.
- [ ] Train Random Forest.
- [ ] Train XGBoost.
- [ ] Evaluate model using AUC and F1.
- [ ] Save best model artifact.

### Backend Engineer

Branch: `feature/api-backend`

Owns:

- FastAPI service.
- Model serving.
- API validation and error handling.
- Prediction response format.

Issues:

- [ ] Set up FastAPI app.
- [ ] Create `/predict` endpoint.
- [ ] Load trained model artifact.
- [ ] Define patient request schema.
- [ ] Return prediction and probabilities.
- [ ] Add SHAP explanation support.
- [ ] Add validation and clear API errors.

### Frontend / UX Engineer

Branch: `feature/frontend-ui`

Owns:

- Clinician-facing interface.
- Patient input flow.
- Risk and explanation display.
- Usability testing.

Issues:

- [ ] Design patient input form.
- [ ] Connect UI to API.
- [ ] Display prediction result.
- [ ] Show risk level: LOW, MEDIUM, HIGH.
- [ ] Show SHAP explanation output.
- [ ] Improve usability for clinical workflows.

## Ready-To-Paste GitHub Issues

### Load And Explore CIDRZ Dataset

Assigned to: Data / ML Engineer  
Branch: `feature/data-preprocessing`

Definition of done:

- [ ] Raw data location documented.
- [ ] Dataset shape and columns summarized.
- [ ] Missingness report created.
- [ ] No patient-identifiable data committed.

### Train Baseline Models

Assigned to: Data / ML Engineer  
Branch: `feature/model-training`

Definition of done:

- [ ] Logistic Regression trained.
- [ ] Random Forest trained.
- [ ] XGBoost trained if dependency and data shape allow it.
- [ ] AUC, F1, and confusion matrix reported.
- [ ] Best model saved under `models/` locally.

### Implement Prediction API

Assigned to: Backend Engineer  
Branch: `feature/api-backend`

Definition of done:

- [ ] `POST /predict` accepts patient data.
- [ ] Endpoint validates required fields.
- [ ] Endpoint loads saved model artifact.
- [ ] Response includes outcome, risk score, risk level, and probabilities.
- [ ] Missing model returns a clear service error.

### Add Patient-Level Explanation

Assigned to: Backend Engineer  
Branch: `feature/shap-explainability`

Definition of done:

- [ ] SHAP explainer artifact loading supported.
- [ ] Prediction response includes top contributing features.
- [ ] Explanation gracefully falls back when artifact is missing.
- [ ] Explanation behavior documented.

### Build Clinician UI

Assigned to: Frontend / UX Engineer  
Branch: `feature/frontend-ui`

Definition of done:

- [ ] Patient form captures required API fields.
- [ ] UI calls `/predict`.
- [ ] Risk level is visually clear.
- [ ] Explanation is shown in plain clinical language.
- [ ] Manual test notes or screenshots included in PR.
