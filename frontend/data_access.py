"""Dataset access for the Streamlit app."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from data.external.circular_data_gen import generate_dataset  # type: ignore
except ModuleNotFoundError:
    generate_dataset = None


@st.cache_data(show_spinner=False)
def load_reconstructed_mock_data() -> pd.DataFrame | None:
    if generate_dataset is None:
        return None
    return generate_dataset()
