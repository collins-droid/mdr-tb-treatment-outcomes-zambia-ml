# Contributing

## Branch Strategy

Use this branch model:

```text
main        production-ready code
staging     integration and release testing
feature/*   individual work branches
```

Recommended feature branches:

```text
feature/model-training
feature/api-backend
feature/frontend-ui
feature/shap-explainability
feature/data-preprocessing
```

Do not push directly to `main` or `staging`. Open a pull request into `staging`, test there, then promote stable changes into `main`.

### Migrating Away From A Single `feature` Branch

Git cannot have both a branch named `feature` and branches named `feature/...` at the same time. If the old `feature` branch is not needed, delete it after confirming with the team:

```bash
git branch -d feature
git push origin --delete feature
```

If it contains work that must be preserved, rename it first:

```bash
git branch -m feature feature/legacy
git push origin feature/legacy
git push origin --delete feature
```

## Workflow

1. Create or pick a GitHub issue.
2. Create the matching `feature/*` branch.
3. Make focused changes.
4. Run relevant tests or manual checks.
5. Open a pull request into `staging`.
6. Request review.
7. Merge only after review and checks pass.

## Team Ownership

| Role | Owns | Main Branch |
| --- | --- | --- |
| Data / ML Engineer | Cleaning, feature engineering, training, evaluation | `feature/model-training` |
| Backend Engineer | FastAPI, model loading, validation, prediction endpoints | `feature/api-backend` |
| Frontend / UX Engineer | Clinician UI, risk display, explanation display | `feature/frontend-ui` |

## Pull Request Rules

Every feature must be testable.

- Data / ML changes should include metrics, saved model path, or reproducible training notes.
- Backend changes should include endpoint checks, schema validation, and error behavior.
- Frontend changes should include screenshots or a clear manual test note.
- Clinical behavior changes should explain risk, assumptions, and validation status.

## Clinical Safety

Never commit real patient data, secrets, or identifiable clinical records. This tool is not approved for patient care until clinically validated.
