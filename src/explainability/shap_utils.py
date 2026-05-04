"""Explanation helpers for prediction responses."""

from __future__ import annotations


FEATURE_LABELS = {
    "age_group": "Age group",
    "gender": "Gender",
    "hiv_status": "HIV status",
    "registration_group": "Registration group",
    "drtb_type": "DR-TB type",
    "district": "District",
}


def clinician_feature_label(feature_name: str) -> str:
    return FEATURE_LABELS.get(feature_name, feature_name.replace("_", " ").title())


def format_explanation(feature: str, effect: str, weight: float) -> dict[str, str | float]:
    """Return the common explanation item shape used by API/UI layers."""
    return {
        "feature": feature,
        "label": clinician_feature_label(feature),
        "effect": effect,
        "weight": weight,
    }
