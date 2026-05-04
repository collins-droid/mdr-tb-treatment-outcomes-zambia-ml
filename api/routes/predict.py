"""Prediction API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas.patient import PatientPredictionRequest, PredictionResponse
from api.services.model_loader import get_model_service


router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("", response_model=PredictionResponse)
def predict_outcome(payload: PatientPredictionRequest) -> PredictionResponse:
    """Return a prototype outcome-risk prediction for one patient."""
    try:
        result = get_model_service().predict(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction service failed") from exc

    return PredictionResponse(
        predicted_outcome=result.predicted_outcome,
        poor_outcome_risk=result.poor_outcome_risk,
        risk_level=result.risk_level,
        probabilities=result.probabilities,
        explanation=[item.__dict__ for item in result.explanation],
        model_version=result.model_version,
        disclaimer=result.disclaimer,
    )
