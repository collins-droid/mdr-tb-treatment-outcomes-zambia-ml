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
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --ink: #0f172a;
            --muted: #64748b;
            --line: #e2e8f0;
            --panel: rgba(255, 255, 255, 0.85);
            --soft: rgba(248, 250, 252, 0.6);
            --brand: #2563eb;
            --accent: #3b82f6;
            --warn: #ea580c;
            --danger: #dc2626;
        }

        .stApp { 
            background: linear-gradient(135deg, #f0f4fd 0%, #e0eafc 100%); 
        }
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif !important;
        }

        .block-container { 
            padding-top: 2rem; 
            max-width: 1200px; 
        }

        h1, h2, h3 { color: var(--ink); letter-spacing: -0.02em; font-family: 'Outfit', sans-serif !important; }
        p, label, .stMarkdown, [data-testid="stCaptionContainer"] { color: var(--muted); }

        .tool-header {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255,255,255,0.8);
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        .tool-header:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 50px -10px rgba(37, 99, 235, 0.15);
        }
        .tool-title {
            font-size: 2.8rem;
            line-height: 1.1;
            font-weight: 800;
            margin: 0 0 0.5rem 0;
            background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .tool-subtitle {
            color: var(--muted);
            font-size: 1.1rem;
            font-weight: 400;
        }
        .section-label {
            color: var(--brand);
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
            display: inline-block;
            background: rgba(37, 99, 235, 0.1);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }
        .result-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 20px -5px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .result-card:hover {
            box-shadow: 0 8px 30px -5px rgba(0,0,0,0.08);
            transform: scale(1.01);
        }
        .risk-band {
            border-radius: 12px;
            padding: 1.2rem;
            margin: 0.5rem 0 1rem 0;
            border: 1px solid rgba(226, 232, 240, 0.6);
            background: linear-gradient(135deg, rgba(255,255,255,0.5) 0%, rgba(248, 250, 252, 0.8) 100%);
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.01);
        }
        .risk-low { color: #059669; font-weight: 800; background: rgba(5, 150, 105, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; }
        .risk-medium { color: #ea580c; font-weight: 800; background: rgba(234, 88, 12, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; }
        .risk-high { color: #dc2626; font-weight: 800; background: rgba(220, 38, 38, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; }
        .risk-value {
            font-size: 3.5rem;
            line-height: 1;
            font-weight: 800;
            color: var(--ink);
            margin: 0.5rem 0;
            text-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .small-muted { color: var(--muted); font-size: 0.9rem; font-weight: 500; }
        
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255,255,255,0.9) !important;
            box-shadow: 0 10px 40px -10px rgba(0,0,0,0.05) !important;
            padding: 2rem !important;
        }

        .stButton>button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            height: 3rem !important;
            transition: all 0.2s ease !important;
            border: none !important;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            color: white !important;
            box-shadow: 0 4px 15px -3px rgba(37, 99, 235, 0.4) !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px -5px rgba(37, 99, 235, 0.5) !important;
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(255,255,255,0.8);
            border-radius: 16px;
            padding: 16px 20px;
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px -5px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
        }
        
        .footer {
            border-top: 1px solid rgba(226, 232, 240, 0.8);
            margin-top: 3rem;
            padding-top: 1.5rem;
            color: var(--muted);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
        }
        
        div[data-testid="stTabs"] button {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
        }
        
        .stAlert { 
            border-radius: 12px; 
            border: none !important;
            box-shadow: 0 4px 15px -5px rgba(0,0,0,0.05);
        }
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

    st.markdown("**SHAP / Feature Log-Odds Contributions**")
    
    # Create a DataFrame for the SHAP/Feature weights to visualize them
    explanation_rows = [
        {"Feature": item["label"], "Impact (Log-Odds)": float(item["weight"])}
        for item in result["explanation"]
    ]
    if explanation_rows:
        explanation_df = pd.DataFrame(explanation_rows)
        # Use a horizontal bar chart
        st.bar_chart(explanation_df, x="Impact (Log-Odds)", y="Feature", horizontal=True, color="#dc2626")
    
    for item in result["explanation"]:
        st.write(f"- **{item['label']}**: {item['effect']}")

    st.caption(str(result["disclaimer"]))


def dataset_panel(df: pd.DataFrame | None) -> None:
    st.markdown('<div class="section-label">Reconstructed Data Review</div>', unsafe_allow_html=True)
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
