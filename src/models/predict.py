"""Shared prediction response helpers for the MDR-TB outcome model."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


PAPER_MORTALITY_RATE = 39 / 183
MALE_AOR = 0.261
AGE_36_45_AOR = 0.253

RISK_THRESHOLDS = {
    "low_max": 0.10,
    "medium_max": 0.20,
}

TREATMENT_OUTCOME_LABELS = (
    "Treatment Success",
    "Died",
    "Lost to Follow Up",
    "Still on Treatment",
)

FEATURE_ORDER = (
    "age_group",
    "gender",
    "hiv_status",
    "registration_group",
    "drtb_type",
    # district excluded: Kabwe aOR=0.544, p=0.401 in Chanda (2024) adjusted regression.
    # It is a case-volume signal, not an independent mortality predictor.
)


@dataclass(frozen=True)
class RiskFactor:
    feature: str
    label: str
    effect: str
    weight: float


@dataclass(frozen=True)
class PredictionResult:
    predicted_outcome: str
    poor_outcome_risk: float
    risk_level: str
    probabilities: dict[str, float]
    explanation: list[RiskFactor]
    model_version: str
    disclaimer: str


def risk_level_from_score(score: float) -> str:
    """Map a numeric poor-outcome score to LOW, MEDIUM, or HIGH."""
    if not isinstance(score, int | float) or not isfinite(score):
        raise ValueError("risk score must be a finite number")
    if score < 0 or score > 1:
        raise ValueError("risk score must be between 0 and 1")
    if score < RISK_THRESHOLDS["low_max"]:
        return "LOW"
    if score < RISK_THRESHOLDS["medium_max"]:
        return "MEDIUM"
    return "HIGH"


def paper_based_mortality_probability(gender: str, age_group: str) -> tuple[float, list[RiskFactor]]:
    """Estimate mortality probability from the paper's significant aORs.

    The calculation anchors to the paper's overall mortality rate and applies
    only the two significant adjusted odds ratios reported in Table 6. This is
    retained as a reference calculation, not as the deployed model path.
    """
    odds = PAPER_MORTALITY_RATE / (1 - PAPER_MORTALITY_RATE)
    factors: list[RiskFactor] = []

    if gender == "Male":
        odds *= MALE_AOR
        factors.append(
            RiskFactor(
                feature="gender",
                label="Male gender",
                effect="Lower adjusted death odds than the female reference group.",
                weight=MALE_AOR,
            )
        )
    else:
        factors.append(
            RiskFactor(
                feature="gender",
                label="Female gender",
                effect="Reference group with higher adjusted mortality in the paper.",
                weight=1.0,
            )
        )

    if age_group == "36-45":
        odds *= AGE_36_45_AOR
        factors.append(
            RiskFactor(
                feature="age_group",
                label="Age 36-45",
                effect="Lower adjusted death odds than the >45 reference group.",
                weight=AGE_36_45_AOR,
            )
        )
    elif age_group == "Above45":
        factors.append(
            RiskFactor(
                feature="age_group",
                label="Age above 45",
                effect="Reference age group with higher adjusted mortality in the paper.",
                weight=1.0,
            )
        )
    else:
        factors.append(
            RiskFactor(
                feature="age_group",
                label=f"Age {age_group}",
                effect="No significant adjusted effect was embedded for this age band.",
                weight=0.0,
            )
        )

    probability = odds / (1 + odds)
    return float(probability), factors


def predict_patient_risk(patient: dict[str, object]) -> PredictionResult:
    """Return a complete prototype prediction payload for one patient."""
    gender = str(patient["gender"])
    age_group = str(patient["age_group"])
    mortality, factors = paper_based_mortality_probability(gender, age_group)

    ltfu_risk = 11 / 183
    poor_outcome_risk = min(1.0, mortality + ltfu_risk)
    success_probability = max(0.0, 1.0 - poor_outcome_risk)
    still_on_treatment_probability = 18 / 183

    probabilities = {
        "Treatment Success": round(success_probability, 4),
        "Died": round(mortality, 4),
        "Lost to Follow Up": round(ltfu_risk, 4),
        "Still on Treatment": round(still_on_treatment_probability, 4),
    }
    total = sum(probabilities.values())
    probabilities = {key: round(value / total, 4) for key, value in probabilities.items()}

    predicted_outcome = max(probabilities, key=probabilities.get)
    return PredictionResult(
        predicted_outcome=predicted_outcome,
        poor_outcome_risk=round(poor_outcome_risk, 4),
        risk_level=risk_level_from_score(poor_outcome_risk),
        probabilities=probabilities,
        explanation=factors,
        model_version="paper-aor-reference-v0",
        disclaimer=(
            "Reference calculation only. The deployed application path uses the "
            "trained outcome model artifact."
        ),
    )
