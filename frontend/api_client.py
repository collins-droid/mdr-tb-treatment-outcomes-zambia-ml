"""Client helpers for the Streamlit frontend."""

from __future__ import annotations

import requests

from api.services.model_loader import get_model_service


def predict_with_api(api_url: str, payload: dict[str, object]) -> dict[str, object]:
    """Call the FastAPI prediction endpoint."""
    response = requests.post(f"{api_url.rstrip('/')}/predict", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def predict_locally(payload: dict[str, object]) -> dict[str, object]:
    """Use the trained outcome model service without an API server."""
    result = get_model_service().predict(payload)
    return {
        "predicted_outcome": result.predicted_outcome,
        "poor_outcome_risk": result.poor_outcome_risk,
        "risk_level": result.risk_level,
        "probabilities": result.probabilities,
        "explanation": [item.__dict__ for item in result.explanation],
        "model_version": result.model_version,
        "disclaimer": result.disclaimer,
    }


def check_api_health(api_url: str) -> tuple[bool, str]:
    try:
        response = requests.get(f"{api_url.rstrip('/')}/health", timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        return False, str(exc)
    return True, response.json().get("version", "unknown")
