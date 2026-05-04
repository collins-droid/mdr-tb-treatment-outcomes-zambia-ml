"""Reusable Streamlit UI components."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.config import (
    AGE_GROUPS,
    DISTRICTS,
    DRTB_TYPES,
    GENDERS,
    HIV_STATUSES,
    LOGO_PATH,
    REGISTRATION_GROUPS,
)


def apply_page_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #172033;
            --muted: #5f6b7a;
            --line: #d9dee7;
            --panel: #ffffff;
            --soft: #f6f8fb;
            --brand: #14532d;
            --accent: #2563eb;
            --warn: #92400e;
            --danger: #991b1b;
        }

        .stApp { background: #f4f7fb; }
        .block-container { padding-top: 1.25rem; max-width: 1240px; }

        h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
        p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--muted); }

        .tool-header {
            border-bottom: 1px solid var(--line);
            padding: 0.25rem 0 1rem 0;
            margin-bottom: 1rem;
        }
        .tool-title {
            font-size: 1.95rem;
            line-height: 1.2;
            font-weight: 720;
            color: var(--ink);
            margin: 0;
        }
        .tool-subtitle {
            color: var(--muted);
            margin-top: 0.35rem;
            font-size: 0.98rem;
        }
        .section-label {
            color: var(--brand);
            font-size: 0.78rem;
            font-weight: 720;
            text-transform: uppercase;
            margin-bottom: 0.15rem;
        }
        .result-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            padding: 1rem;
            margin-bottom: 0.9rem;
        }
        .risk-band {
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin: 0.3rem 0 0.9rem 0;
            border: 1px solid var(--line);
            background: var(--soft);
        }
        .risk-low { color: #166534; font-weight: 760; }
        .risk-medium { color: var(--warn); font-weight: 760; }
        .risk-high { color: var(--danger); font-weight: 760; }
        .risk-value {
            font-size: 2.25rem;
            line-height: 1.05;
            font-weight: 760;
            color: var(--ink);
        }
        .small-muted { color: var(--muted); font-size: 0.88rem; }
        .footer {
            border-top: 1px solid var(--line);
            margin-top: 2rem;
            padding-top: 1rem;
            color: var(--muted);
            font-size: 0.86rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px 14px;
            background: var(--panel);
        }
        div[data-testid="stTabs"] button p { font-size: 0.95rem; }
        .stAlert { border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header() -> None:
    st.markdown(
        """
        <div class="tool-header">
            <div class="section-label">MDR-TB clinical decision-support prototype</div>
            <div class="tool-title">Treatment Outcome Risk Assessment</div>
            <div class="tool-subtitle">
                Enter patient characteristics, review the poor-outcome risk level, and inspect the factors used by the trained outcome model.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def patient_form() -> dict[str, object] | None:
    st.markdown('<div class="section-label">Patient intake</div>', unsafe_allow_html=True)
    with st.form("patient_assessment_form", clear_on_submit=False, border=True):
        top = st.columns(2)
        with top[0]:
            age_group = st.selectbox("Age group", AGE_GROUPS, index=3)
            gender = st.radio("Gender", GENDERS, horizontal=True)
            hiv_status = st.selectbox("HIV status", HIV_STATUSES)
        with top[1]:
            registration_group = st.selectbox("Registration group", REGISTRATION_GROUPS)
            drtb_type = st.selectbox("DR-TB type", DRTB_TYPES)
            district = st.selectbox("District", DISTRICTS)

        year_of_diagnosis = st.number_input(
            "Year of diagnosis",
            min_value=2017,
            max_value=2026,
            value=2021,
            step=1,
        )
        submitted = st.form_submit_button("Assess patient", type="primary", use_container_width=True)

    if not submitted:
        return None

    return {
        "age_group": age_group,
        "gender": gender,
        "hiv_status": hiv_status,
        "registration_group": registration_group,
        "drtb_type": drtb_type,
        "district": district,
        "year_of_diagnosis": int(year_of_diagnosis),
    }


def empty_result_panel() -> None:
    st.markdown('<div class="section-label">Assessment result</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="result-card">
            <div class="small-muted">
                Complete the patient intake form and run an assessment to view risk level, predicted outcome,
                probability distribution, and explanation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prediction_panel(result: dict[str, object], source: str) -> None:
    st.markdown('<div class="section-label">Assessment result</div>', unsafe_allow_html=True)
    level = str(result["risk_level"])
    css_class = {"LOW": "risk-low", "MEDIUM": "risk-medium", "HIGH": "risk-high"}[level]
    risk = float(result["poor_outcome_risk"])

    st.markdown(
        f"""
        <div class="result-card">
            <div class="small-muted">Poor-outcome risk</div>
            <div class="risk-value">{risk:.1%}</div>
            <div class="risk-band">
                Risk level: <span class="{css_class}">{level}</span><br>
                Likely outcome: <strong>{result["predicted_outcome"]}</strong>
            </div>
            <div class="small-muted">Source: {source} | Model: {result["model_version"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    probability_rows = [
        {"Outcome": key, "Probability": value}
        for key, value in dict(result["probabilities"]).items()
    ]
    probabilities = pd.DataFrame(probability_rows)

    st.markdown("**Outcome probabilities**")
    st.dataframe(
        probabilities.assign(Probability=probabilities["Probability"].map(lambda value: f"{value:.1%}")),
        use_container_width=True,
        hide_index=True,
    )
    st.bar_chart(probabilities, x="Outcome", y="Probability", color="#2563eb")

    st.markdown("**Factors used by the trained model**")
    for item in result["explanation"]:
        st.write(f"- **{item['label']}**: {item['effect']}")

    st.caption(str(result["disclaimer"]))


def dataset_panel(df: pd.DataFrame | None) -> None:
    st.markdown('<div class="section-label">Mock data review</div>', unsafe_allow_html=True)
    st.subheader("Reconstructed Aggregate-Count Dataset")
    if df is None:
        st.warning(
            "The local reconstruction generator is not available in this deployment. "
            "Add a reviewed, tracked mock-data module before enabling dataset preview in hosted environments."
        )
        return

    cols = st.columns(5)
    cols[0].metric("Rows", f"{len(df)}")
    cols[1].metric("Deaths", int(df["died"].sum()))
    cols[2].metric("Treatment success", int(df["treatment_success"].sum()))
    cols[3].metric("Lost to follow-up", int(df["lost_to_followup"].sum()))
    cols[4].metric("Mean age", f"{df['age_years'].mean():.1f}")

    chart_data = df["outcome"].value_counts().rename_axis("outcome").reset_index(name="count")
    st.bar_chart(chart_data, x="outcome", y="count", color="#2563eb")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="drtb_central_zambia_reconstructed_mock.csv",
        mime="text/csv",
    )


def validity_panel() -> None:
    st.markdown('<div class="section-label">Validation boundary</div>', unsafe_allow_html=True)
    st.subheader("What This Prototype Can And Cannot Support")

    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Appropriate use**")
        st.write(
            "- Demonstrating the application workflow.\n"
            "- Testing API, frontend, and data-column handling.\n"
            "- Showing a patient-like table reconstructed from published aggregate counts."
        )
    with cols[1]:
        st.markdown("**Not appropriate use**")
        st.write(
            "- Clinical decision-making.\n"
            "- Model training for deployment.\n"
            "- Reproducing or validating the paper's adjusted odds ratios.\n"
            "- Treating reconstructed rows as independent synthetic patient records."
        )

    st.markdown("**Methodological notes**")
    st.write(
        "- Many cross-variable relationships were not published, so row-level correlations are invented by allocation.\n"
        "- The mortality predictors are not generated from a full fitted probability model.\n"
        "- The paper reports incomplete 2021 outcome evaluation, so row-level 2021 outcomes require explicit caution.\n"
        "- Continuous ages are assumptions inside published age bands, not recovered observations."
    )


def footer_logo() -> None:
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    cols = st.columns([0.72, 0.28], vertical_alignment="center")
    with cols[0]:
        st.caption(
            "MDR-TB Treatment Outcomes Predictor | Research prototype for controlled review and demonstration."
        )
    with cols[1]:
        st.image(LOGO_PATH, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
