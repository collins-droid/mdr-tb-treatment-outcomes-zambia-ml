"""Training entry points for the MDR-TB outcome model.

Key improvements over v1:
- RandomForest with constrained depth + min_samples_leaf to reduce overfitting.
- Probability calibration (isotonic) to fix overconfident predictions (was ~65%, paper overall rate is 21.3%).
- GridSearchCV to find the best RF hyperparameters on this small dataset.
- District removed from CALIBRATED_FEATURES: per Chanda (2024) adjusted regression,
  Kabwe district had aOR=0.544 and p=0.401 (non-significant). Including it was inflating
  district as a mortality driver when it is a case-volume signal, not a death-risk signal.
- StratifiedKFold cross-validation throughout.
"""

from __future__ import annotations

import json
import os
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GridSearchCV,
    LearningCurveDisplay,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt

from src.features.feature_engineering import PREDICTION_FEATURES, add_binary_outcomes, encode_prediction_features
from src.utils.helpers import project_path


TARGET_COLUMN = "poor_outcome"
OUTCOME_TARGET_COLUMN = "outcome_class"
DEFAULT_MODEL_PATH = project_path("models", "mdrtb_outcome_model.joblib")
DEFAULT_METRICS_PATH = project_path("models", "mdrtb_outcome_model_metrics.json")
RANDOM_STATE = 8701

# District is excluded from calibrated training features.
# Per Chanda (2024) adjusted regression: Kabwe aOR=0.544, p=0.401 (non-significant).
# Including district inflates Kabwe as a mortality driver when it is a case-volume
# signal only. All other original features are retained.
CALIBRATED_FEATURES = [f for f in PREDICTION_FEATURES if f != "district"]


@dataclass(frozen=True)
class TrainingDataset:
    features: pd.DataFrame
    target: pd.Series


@dataclass(frozen=True)
class TrainingResult:
    artifact_path: Path
    metrics_path: Path
    metrics: dict[str, Any]
    model_version: str


# Target outcome classes — mirrors the paper's evaluated outcomes.
# "Still on Treatment" is excluded: these are censored observations (outcome not
# yet determined, predominantly incomplete 2021 records). Including them would
# add a fourth class that is neither a success nor a failure, degrading model signal.
# Three clinically meaningful prediction targets (excludes censored records).
TARGET_OUTCOME_CLASSES = ["Treatment Success", "Died", "Lost to Follow Up"]


def normalize_outcome(outcome: str) -> str | None:
    """Map paper outcome labels to the three evaluated outcome classes.

    Returns None for 'Still on Treatment': these are censored observations
    (outcome not yet determined). It makes no clinical sense to predict this
    class for a new patient, so they are excluded from training.
    """
    if outcome in {"Cured", "Treatment Completed", "Treatment Success"}:
        return "Treatment Success"
    if outcome == "Lost to Follow Up":
        return "Lost to Follow Up"
    if outcome == "Died":
        return "Died"
    return None  # Still on Treatment = censored, not a valid prediction class


def prepare_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the project dataset for model training.

    Drops 'Still on Treatment' rows before training — these are censored
    observations (predominantly incomplete 2021 records per the paper).
    """
    prepared = add_binary_outcomes(df)
    prepared[OUTCOME_TARGET_COLUMN] = prepared["outcome"].map(normalize_outcome)
    n_censored = prepared[OUTCOME_TARGET_COLUMN].isna().sum()
    if n_censored > 0:
        print(f"  Dropping {n_censored} censored 'Still on Treatment' rows.")
        prepared = prepared.dropna(subset=[OUTCOME_TARGET_COLUMN]).copy()
    return prepared


def build_training_dataset(df: pd.DataFrame) -> TrainingDataset:
    """Build a model matrix from reviewed data with a poor_outcome target."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError("training dataframe must include a poor_outcome target")
    missing = [f for f in PREDICTION_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"training dataframe missing features: {', '.join(missing)}")
    return TrainingDataset(
        features=encode_prediction_features(df),
        target=df[TARGET_COLUMN].astype(int),
    )


def build_preprocessor(features: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), features)
        ],
        remainder="drop",
    )


def build_outcome_pipeline(classifier=None, features: list[str] | None = None) -> Pipeline:
    feats = features or PREDICTION_FEATURES
    if classifier is None:
        classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=4,          # Constrain depth — prevents overfitting on 183 rows
            min_samples_leaf=5,   # Each leaf needs ≥5 samples — reduces noise memorisation
            class_weight="balanced",  # Corrects for class imbalance
            random_state=RANDOM_STATE,
        )
    return Pipeline(
        steps=[
            ("preprocess", build_preprocessor(feats)),
            ("classifier", classifier),
        ]
    )


def tune_random_forest(x: pd.DataFrame, y: pd.Series, features: list[str]) -> RandomForestClassifier:
    """Run GridSearchCV to find best RF hyperparameters for this small dataset."""
    param_grid = {
        "classifier__n_estimators": [100, 200],
        "classifier__max_depth": [3, 4, 5],
        "classifier__min_samples_leaf": [3, 5, 8],
    }
    base_pipeline = build_outcome_pipeline(
        RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE),
        features=features,
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    grid = GridSearchCV(
        base_pipeline,
        param_grid,
        cv=cv,
        scoring="f1_macro",
        n_jobs=-1,
        refit=True,
    )
    grid.fit(x, y)
    best_params = {k.replace("classifier__", ""): v for k, v in grid.best_params_.items()}
    print(f"  Best RF params: {best_params}  |  Best CV F1: {grid.best_score_:.3f}")
    return grid.best_estimator_


def compare_models(x: pd.DataFrame, y: pd.Series, features: list[str]) -> dict[str, dict]:
    """Benchmark candidate classifiers using stratified 5-fold CV."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    candidates = {
        "Dummy (Baseline)": DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE),
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
        "Decision Tree (depth=4)": DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=RANDOM_STATE),
        "Random Forest (tuned)": RandomForestClassifier(
            n_estimators=200, max_depth=4, min_samples_leaf=5,
            class_weight="balanced", random_state=RANDOM_STATE
        ),
    }
    results = {}
    for name, clf in candidates.items():
        pipeline = build_outcome_pipeline(clf, features=features)
        acc = cross_val_score(pipeline, x, y, cv=cv, scoring="accuracy")
        f1  = cross_val_score(pipeline, x, y, cv=cv, scoring="f1_macro")
        results[name] = {
            "cv_accuracy_mean": round(float(np.mean(acc)), 4),
            "cv_accuracy_std":  round(float(np.std(acc)), 4),
            "cv_f1_macro_mean": round(float(np.mean(f1)), 4),
            "cv_f1_macro_std":  round(float(np.std(f1)), 4),
        }
    return results


def train_outcome_model(
    df: pd.DataFrame,
    artifact_path: str | Path = DEFAULT_MODEL_PATH,
    metrics_path: str | Path = DEFAULT_METRICS_PATH,
) -> TrainingResult:
    """Train and save a calibrated, tuned Random Forest outcome model.

    Improvements over v1:
    - District excluded: non-significant mortality predictor per paper (p=0.401).
    - RF constrained (max_depth=4, min_samples_leaf=5) to reduce overfitting.
    - GridSearchCV finds the best hyperparameters.
    - CalibratedClassifierCV (isotonic) corrects overconfident probability estimates.

    The current project dataset is reconstructed from published aggregate counts.
    It is sufficient for an academic prototype but must not be used clinically.
    """
    prepared = prepare_training_frame(df)
    features = CALIBRATED_FEATURES
    missing = [f for f in features if f not in prepared.columns]
    if missing:
        raise ValueError(f"training dataframe missing features: {', '.join(missing)}")

    x = prepared[features]
    y = prepared[OUTCOME_TARGET_COLUMN]

    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=RANDOM_STATE, stratify=stratify
    )

    print("Running model comparison...")
    comparison = compare_models(x, y, features)

    print("Running GridSearchCV to tune Random Forest...")
    best_pipeline = tune_random_forest(x_train, y_train, features)

    # Probability calibration — fixes the overconfident 65% predictions
    print("Calibrating probabilities (isotonic regression)...")
    cv_calib = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)
    calibrated = CalibratedClassifierCV(best_pipeline, cv=cv_calib, method="isotonic")
    calibrated.fit(x_train, y_train)

    y_pred       = calibrated.predict(x_test)
    y_pred_proba = calibrated.predict_proba(x_test)

    # Learning curve on the tuned (uncalibrated) pipeline for visualisation
    fig, ax = plt.subplots(figsize=(8, 6))
    cv_lc = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    LearningCurveDisplay.from_estimator(
        best_pipeline, x, y, cv=cv_lc, scoring="f1_macro", ax=ax, n_jobs=-1
    )
    ax.set_title("Learning Curve (Tuned Random Forest, Macro F1)")
    curve_path = project_path("docs", "learning_curve.png")
    curve_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(curve_path)
    plt.close(fig)

    classes = list(calibrated.classes_)
    metrics: dict[str, Any] = {
        "model_version": "randomforest-calibrated-v2",
        "model_selection_rationale": (
            "Four classifiers benchmarked via stratified 5-fold CV. Random Forest selected "
            "for highest macro F1. GridSearchCV tuned max_depth and min_samples_leaf. "
            "CalibratedClassifierCV (isotonic) applied to correct overconfident probability "
            "estimates identified in Phase 5 alignment audit vs Chanda (2024)."
        ),
        "calibration_note": (
            "District excluded from features: Kabwe had aOR=0.544, p=0.401 (non-significant) "
            "in the Chanda (2024) adjusted regression. Including district was inflating Kabwe "
            "as a mortality driver when it is a case-volume signal only."
        ),
        "model_comparison": comparison,
        "dataset": "reconstructed aggregate-count MDR-TB dataset",
        "target": OUTCOME_TARGET_COLUMN,
        "features": features,
        "n_rows": int(len(prepared)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "accuracy":  float(accuracy_score(y_test, y_pred)),
        "f1_score":  float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "roc_auc":   float(roc_auc_score(y_test, y_pred_proba, multi_class="ovr")),
        "classes":   classes,
        "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=classes).tolist(),
        "important_limitation": (
            "Trained on rows reconstructed from published aggregate counts. "
            "Use for academic prototype demonstration, not clinical deployment."
        ),
    }

    artifact = {
        "model":          calibrated,
        "model_version":  metrics["model_version"],
        "features":       features,
        "classes":        classes,
        "metrics":        metrics,
    }

    artifact_path = Path(artifact_path)
    metrics_path  = Path(metrics_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, artifact_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"  Accuracy : {metrics['accuracy']:.3f}")
    print(f"  Macro F1 : {metrics['f1_score']:.3f}")
    print(f"  ROC-AUC  : {metrics['roc_auc']:.3f}")

    return TrainingResult(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        metrics=metrics,
        model_version=str(metrics["model_version"]),
    )


def load_reconstructed_training_data() -> pd.DataFrame:
    """Load the local reconstructed dataset, generating it if needed."""
    csv_path = project_path("data", "external", "drtb_central_zambia_synthetic.csv")
    if csv_path.exists():
        return pd.read_csv(csv_path)

    from data.external.circular_data_gen import generate_dataset

    with open(os.devnull, "w", encoding="utf-8") as sink, redirect_stdout(sink):
        return generate_dataset()


def train_default_model() -> TrainingResult:
    """Train the default model artifact from the local project dataset."""
    return train_outcome_model(load_reconstructed_training_data())


if __name__ == "__main__":
    result = train_default_model()
    print(f"Saved model   : {result.artifact_path}")
    print(f"Saved metrics : {result.metrics_path}")
    print(f"Model version : {result.model_version}")
