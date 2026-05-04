"""Training entry points for the MDR-TB outcome model."""

from __future__ import annotations

import json
import os
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.features.feature_engineering import PREDICTION_FEATURES, add_binary_outcomes, encode_prediction_features
from src.utils.helpers import project_path


TARGET_COLUMN = "poor_outcome"
OUTCOME_TARGET_COLUMN = "outcome_class"
DEFAULT_MODEL_PATH = project_path("models", "mdrtb_outcome_model.joblib")
DEFAULT_METRICS_PATH = project_path("models", "mdrtb_outcome_model_metrics.json")
RANDOM_STATE = 8701


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


def normalize_outcome(outcome: str) -> str:
    """Map paper outcome labels to application outcome classes."""
    if outcome in {"Cured", "Treatment Completed", "Treatment Success"}:
        return "Treatment Success"
    if outcome == "Lost to Follow Up":
        return "Lost to Follow Up"
    if outcome == "Died":
        return "Died"
    return "Still on Treatment"


def prepare_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the project dataset for model training."""
    prepared = add_binary_outcomes(df)
    prepared[OUTCOME_TARGET_COLUMN] = prepared["outcome"].map(normalize_outcome)
    if prepared[OUTCOME_TARGET_COLUMN].isna().any():
        raise ValueError("training data contains unsupported outcome labels")
    return prepared


def build_training_dataset(df: pd.DataFrame) -> TrainingDataset:
    """Build a model matrix from reviewed data with a poor_outcome target."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError("training dataframe must include a poor_outcome target")
    missing = [feature for feature in PREDICTION_FEATURES if feature not in df.columns]
    if missing:
        raise ValueError(f"training dataframe missing features: {', '.join(missing)}")
    return TrainingDataset(
        features=encode_prediction_features(df),
        target=df[TARGET_COLUMN].astype(int),
    )


def build_outcome_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                PREDICTION_FEATURES,
            )
        ],
        remainder="drop",
    )
    classifier = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_outcome_model(
    df: pd.DataFrame,
    artifact_path: str | Path = DEFAULT_MODEL_PATH,
    metrics_path: str | Path = DEFAULT_METRICS_PATH,
) -> TrainingResult:
    """Train and save a multiclass logistic-regression outcome model.

    The current project dataset is reconstructed from published aggregate
    counts. It is enough for a working academic prototype and reproducible
    software demonstration, but it is not a substitute for external clinical
    validation on independently collected patient records.
    """
    prepared = prepare_training_frame(df)
    missing = [feature for feature in PREDICTION_FEATURES if feature not in prepared.columns]
    if missing:
        raise ValueError(f"training dataframe missing features: {', '.join(missing)}")

    x = prepared[PREDICTION_FEATURES]
    y = prepared[OUTCOME_TARGET_COLUMN]
    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )

    pipeline = build_outcome_pipeline()
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)

    metrics: dict[str, Any] = {
        "model_version": "logistic-reconstruction-v1",
        "dataset": "reconstructed aggregate-count MDR-TB dataset",
        "target": OUTCOME_TARGET_COLUMN,
        "features": PREDICTION_FEATURES,
        "n_rows": int(len(prepared)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "classes": list(pipeline.named_steps["classifier"].classes_),
        "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=list(pipeline.named_steps["classifier"].classes_)).tolist(),
        "important_limitation": (
            "Trained on rows reconstructed from published aggregate counts. "
            "Use for academic prototype demonstration, not clinical deployment."
        ),
    }

    artifact = {
        "model": pipeline,
        "model_version": metrics["model_version"],
        "features": PREDICTION_FEATURES,
        "classes": metrics["classes"],
        "metrics": metrics,
    }

    artifact_path = Path(artifact_path)
    metrics_path = Path(metrics_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, artifact_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

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
    print(f"Saved model: {result.artifact_path}")
    print(f"Saved metrics: {result.metrics_path}")
    print(f"Accuracy: {result.metrics['accuracy']:.3f}")
