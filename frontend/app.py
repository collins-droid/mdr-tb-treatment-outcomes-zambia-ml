"""Streamlit entry point for the MDR-TB outcome prototype."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so absolute imports work in Streamlit Cloud
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests
import streamlit as st

from frontend.api_client import check_api_health, predict_locally, predict_with_api
from frontend.components import (
    apply_page_styles,
    dataset_panel,
    empty_result_panel,
    footer_logo,
    page_header,
    patient_form,
    prediction_panel,
    validity_panel,
)
from frontend.config import DEFAULT_API_URL, VALIDITY_WARNING
from frontend.data_access import load_reconstructed_mock_data


st.set_page_config(
    page_title="MDR-TB Outcome Risk Prototype",
    layout="wide",
)
apply_page_styles()

page_header()
st.warning(VALIDITY_WARNING)

with st.sidebar:
    st.header("System")
    use_api = st.toggle("Use FastAPI backend", value=False)
    api_url = st.text_input("API URL", DEFAULT_API_URL, disabled=not use_api)
    if use_api:
        ok, detail = check_api_health(api_url)
        if ok:
            st.success(f"API online, version {detail}")
        else:
            st.error(f"API unavailable: {detail}")
    else:
        st.info("Using local trained outcome model.")

tab_screen, tab_data, tab_validity = st.tabs(["Assessment", "Reconstructed Dataset", "Validation Notes"])

with tab_screen:
    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        payload = patient_form()

    with right:
        if payload is None:
            empty_result_panel()
        else:
            try:
                if use_api:
                    prediction = predict_with_api(api_url, payload)
                    source = "FastAPI"
                else:
                    prediction = predict_locally(payload)
                    source = "Local trained model"
                prediction_panel(prediction, source)
            except requests.RequestException as exc:
                st.error(f"Prediction API request failed: {exc}")
            except Exception as exc:
                st.error(f"Prediction failed: {exc}")

            with st.expander("Assessment payload", expanded=False):
                st.json(payload)

with tab_data:
    dataset_panel(load_reconstructed_mock_data())

with tab_validity:
    validity_panel()

footer_logo()
