"""Preprocessing pipeline entry point."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.cleaning import clean_patient_dataframe
from src.features.feature_engineering import add_binary_outcomes


BLOCKED_IDENTIFIER_COLUMNS = {"name", "nrc", "phone", "address", "patient_name"}


def assert_no_obvious_identifiers(df: pd.DataFrame) -> None:
    found = sorted(BLOCKED_IDENTIFIER_COLUMNS & set(df.columns))
    if found:
        raise ValueError(f"potential identifier columns are not allowed: {', '.join(found)}")


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_patient_dataframe(df)
    assert_no_obvious_identifiers(cleaned)
    return add_binary_outcomes(cleaned)


def preprocess_csv(input_path: str | Path, output_path: str | Path) -> Path:
    processed = preprocess_dataframe(pd.read_csv(input_path))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output, index=False)
    return output
