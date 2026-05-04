"""API schemas for patient prediction requests and responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AgeGroup = Literal["0-15", "16-25", "26-35", "36-45", "Above45"]
Gender = Literal["Male", "Female"]
HivStatus = Literal["Positive", "Negative", "Unknown"]
RegistrationGroup = Literal["New", "Relapse", "After loss to FU", "Transfer in", "Other"]
DrtbType = Literal["RR-TB", "MDR-TB", "IR-TB", "XDR-TB"]
District = Literal[
    "Kabwe",
    "Kapiri Mposhi",
    "Chibombo",
    "Chisamba",
    "Mumbwa",
    "Mkushi",
    "Serenje",
    "Chitambo",
    "Other",
]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class PatientPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age_group: AgeGroup
    gender: Gender
    hiv_status: HivStatus
    registration_group: RegistrationGroup
    drtb_type: DrtbType
    district: District
    year_of_diagnosis: int | None = Field(default=None, ge=2017, le=2026)


class ExplanationItem(BaseModel):
    feature: str
    label: str
    effect: str
    weight: float


class PredictionResponse(BaseModel):
    predicted_outcome: str
    poor_outcome_risk: float = Field(ge=0, le=1)
    risk_level: RiskLevel
    probabilities: dict[str, float]
    explanation: list[ExplanationItem]
    model_version: str
    disclaimer: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
