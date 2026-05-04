"""Feature engineering helpers for the MDR-TB prototype."""

from __future__ import annotations

import pandas as pd


PREDICTION_FEATURES = [
    "age_group",
    "gender",
    "hiv_status",
    "registration_group",
    "drtb_type",
    "district",
]


def add_binary_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """Add common binary outcome columns used by evaluation and demos."""
    engineered = df.copy()
    engineered["died"] = (engineered["outcome"] == "Died").astype(int)
    engineered["lost_to_followup"] = (engineered["outcome"] == "Lost to Follow Up").astype(int)
    engineered["treatment_success"] = engineered["outcome"].isin(
        ["Cured", "Treatment Completed", "Treatment Success"]
    ).astype(int)
    engineered["poor_outcome"] = engineered["outcome"].isin(["Died", "Lost to Follow Up"]).astype(int)
    return engineered


def encode_prediction_features(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode the current approved prediction-time fields."""
    missing = [feature for feature in PREDICTION_FEATURES if feature not in df.columns]
    if missing:
        raise ValueError(f"missing prediction features: {', '.join(missing)}")
    return pd.get_dummies(df[PREDICTION_FEATURES], drop_first=False, dtype=int)
