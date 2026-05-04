"""Tests for training the reconstructed-data outcome model."""

from pathlib import Path

from data.external.circular_data_gen import generate_dataset
from src.models.train import train_outcome_model


def test_train_outcome_model_writes_artifacts(tmp_path: Path) -> None:
    result = train_outcome_model(
        generate_dataset(),
        artifact_path=tmp_path / "model.joblib",
        metrics_path=tmp_path / "metrics.json",
    )

    assert result.artifact_path.exists()
    assert result.metrics_path.exists()
    assert result.metrics["n_rows"] == 183
    assert result.metrics["classes"]
