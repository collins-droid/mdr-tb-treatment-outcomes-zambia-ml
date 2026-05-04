"""Data cleaning utilities for MDR-TB outcome modeling."""

from __future__ import annotations

import re

import pandas as pd


REQUIRED_COLUMNS = {
    "age_group",
    "gender",
    "hiv_status",
    "registration_group",
    "drtb_type",
    "district",
    "outcome",
}


def standardize_column_name(name: str) -> str:
    """Convert a raw column name into a safe snake_case identifier."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip().lower())
    return cleaned.strip("_")


def clean_patient_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a lightly cleaned dataframe with required modeling columns.

    This does not de-identify raw clinical records. Real patient datasets must
    be reviewed before being passed into this project.
    """
    cleaned = df.copy()
    cleaned.columns = [standardize_column_name(col) for col in cleaned.columns]
    missing = sorted(REQUIRED_COLUMNS - set(cleaned.columns))
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    cleaned = cleaned.drop_duplicates()
    for col in cleaned.select_dtypes(include="object").columns:
        cleaned[col] = cleaned[col].str.strip()
    return cleaned
