"""Tests for risk-level behavior."""

import pytest

from src.models.predict import risk_level_from_score


def test_risk_level_boundaries() -> None:
    assert risk_level_from_score(0.0) == "LOW"
    assert risk_level_from_score(0.0999) == "LOW"
    assert risk_level_from_score(0.10) == "MEDIUM"
    assert risk_level_from_score(0.1999) == "MEDIUM"
    assert risk_level_from_score(0.20) == "HIGH"
    assert risk_level_from_score(1.0) == "HIGH"


@pytest.mark.parametrize("score", [-0.1, 1.1, float("nan")])
def test_invalid_risk_scores_raise(score: float) -> None:
    with pytest.raises(ValueError):
        risk_level_from_score(score)

