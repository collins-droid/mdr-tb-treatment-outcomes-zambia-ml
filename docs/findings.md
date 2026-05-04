# Phase 3: Model Evaluation & Selection

## Objective
We benchmarked four candidate classifiers using 5-fold cross-validation before selecting the final model. The goal was to choose the algorithm that performs best on this reconstructed dataset and can be justified with evidence.

## Model Comparison (5-fold Cross-Validation)

| Model | CV Accuracy (Mean ± Std) | CV Macro F1 (Mean ± Std) |
| :--- | :--- | :--- |
| **Dummy (Baseline)** | ~0.46 ± 0.05 | ~0.15 ± 0.02 |
| **Logistic Regression** | ~0.51 ± 0.06 | ~0.18 ± 0.04 |
| **Decision Tree (depth=5)** | ~0.49 ± 0.07 | ~0.17 ± 0.05 |
| **Random Forest (n=100)** | ~0.54 ± 0.05 | ~0.21 ± 0.04 |

> Note: Exact values are logged into `models/mdrtb_outcome_model_metrics.json` under `model_comparison` on each training run.

**Selection Rationale:** Random Forest achieved the highest mean CV accuracy and macro F1-score among all candidates. Logistic Regression performed only marginally better than the dummy baseline due to the lack of true inter-variable correlations in the reconstructed data. Decision Tree showed higher variance (instability). Random Forest's ensemble averaging provides more stable predictions, making it the most defensible choice for a research prototype.

## Findings: Test Set Performance

### 1. Updated Model Performance
After selecting `RandomForestClassifier` (100 estimators), the model performance metrics on the held-out test set (25%) are as follows:
- **Accuracy**: ~54.3%
- **Macro F1-Score**: ~0.211
- **ROC-AUC (OVR)**: ~0.594

### 2. Analysis of the Drop in Accuracy
The drop in raw accuracy is expected. Random Forests are prone to overfitting small datasets (our training set is only 137 rows). While the Random Forest model attempts to find complex interactions between features like `age_group` and `hiv_status`, the underlying dataset is reconstructed from aggregate counts. This means row-level correlations are essentially noise/synthetic allocations rather than genuine physiological patterns. The Random Forest is likely memorizing noise in the training set that does not generalize to the test set.

### 3. Metric Breakdown
- **ROC-AUC (0.594)**: Indicates that the model is only slightly better than random guessing at distinguishing between the four outcome classes. 
- **Macro F1-Score (0.211)**: Highlights the model's severe struggle with minority classes ("Lost to Follow Up" and "Still on Treatment" both have an F1-score of 0.0). The model heavily defaults to the majority class ("Treatment Success") or the most distinct minority class ("Died").

### 4. Training Curves
We generated a cross-validation learning curve (`docs/learning_curve.png`) to visualize the Random Forest's performance over varying sample sizes. The curve confirms high variance (a large gap between training accuracy and cross-validation accuracy), which is a classic indicator of overfitting on small data.

## Conclusion
The baseline Logistic Regression served its purpose by validating the pipeline and establishing a baseline distribution. The Random Forest model exposes the fundamental limitation of the current dataset: complex, non-linear models cannot extract meaningful signals from aggregate-reconstructed synthetic rows.

**Next Steps:**
- Do not attempt further hyperparameter tuning on the synthetic dataset.
- Await the integration of real, correlated patient records before optimizing the Random Forest or switching to XGBoost.
- The UI explainer module has been successfully updated to parse `feature_importances_` from the Random Forest instead of relying on linear coefficients, ensuring the application remains robust regardless of the underlying algorithm.

## Phase 4: Statistical Audit & Clinical Signal Verification

We performed a comprehensive clinical signal audit by comparing our reconstructed mock dataset against the original findings reported in the **Chanda (2024)** research paper.

### 1. Structural Verification: Does the Data Tally?

The totals in our reconstructed dataset match the paper's aggregate counts perfectly:

| Metric | Original Paper (Chanda 2024) | Our Mock Dataset | Status |
| :--- | :--- | :--- | :--- |
| **Total Sample (N)** | 183 | 183 | ✅ Match |
| **Mean Age** | 35.24 years | ~35.2 years | ✅ Match |
| **Gender Balance** | 57.9% Male | 57.9% Male | ✅ Match |
| **Mortality Rate** | 21.3% (39 Deaths) | 21.3% (39 Deaths) | ✅ Match |
| **HIV Prevalence** | 60.7% Positive | 60.7% Positive | ✅ Match |

### 2. Inferential Testing: The "Signal Loss" Discovery

While the **counts** match, the **statistical relationships (signals)** have drifted from the original research due to the reconstruction process:

| Variable | Audit P-Value (Mock Data) | Chanda 2024 P-Value (Original) | Conclusion |
| :--- | :--- | :--- | :--- |
| **HIV Status** | **0.4435** (Non-Sig) | **0.026** (Significant) | **Signal Lost** |
| **Age** | **0.8671** (Non-Sig) | **0.035** (Significant) | **Signal Lost** |
| **Gender** | **<0.05** (Significant) | **0.003** (Significant) | **Signal Preserved** |

- **Why this matters**: In the original study, HIV status was a significant predictor of mortality. In our reconstructed dataset, because outcomes were randomized (shuffled) across HIV statuses to protect privacy while only maintaining total counts, the statistical link is broken.
- **Gender Paradox**: Gender remains significant only because we explicitly "nudged" the death outcomes in the code to match the paper's specific count of 16 Male vs 23 Female deaths.

### 3. Conclusion for Research Use
Our dataset is a perfect **structural replica** (it looks right and has the right proportions), but it is a **clinical ghost**. It correctly simulates the environment of the Central Province, but the model cannot "re-discover" the HIV signal because that signal was randomized during reconstruction. 

This confirms that the model's predictions on this mock data are for **software demonstration and pipeline testing only**, as they lack the true joint-probability structure of real patient data.


## Phase 5: Model Alignment Audit — Predictions vs. Chanda (2024)

This section critically compares the model's output behaviour against the adjusted statistical findings in the original paper.

### 1. Where the Model Agrees with the Paper

| Finding | Paper | Model | Status |
| :--- | :--- | :--- | :--- |
| **Death is a major outcome** | 21.3% mortality | Predicts death risk prominently | ✅ Directionally correct |
| **Kabwe = DR-TB burden hotspot** | 60.7% of cases from Kabwe | Kabwe contributes to predictions | ✅ Correct (case volume) |
| **HIV positivity is common** | 60.7% HIV-positive | HIV-positive contributes to model | ✅ Prevalence-correct |
| **Adult age groups predominate** | Mean age 35.24 | Age group features are active | ✅ Correct |

### 2. Where the Model Conflicts with the Paper

| Variable | Paper's Adjusted Finding | Model Behaviour | Verdict |
| :--- | :--- | :--- | :--- |
| **Kabwe District** | aOR=0.544, **p=0.401** (non-significant) | Treated as a strong death-risk driver | ❌ **Conflict** — Kabwe predicts burden, not mortality |
| **HIV Status** | aOR not significant for death (**p=0.069**) | Assigned a strong positive contribution | ⚠️ **Overclaims** — plausible but not paper-supported |
| **Female Gender** | Male aOR=0.261, **p=0.003** (female = higher raw deaths, but regression uses female as reference) | `gender Female` appears as positive risk contributor | ⚠️ **Partially aligned** — aligns with descriptive counts, not adjusted regression |
| **65% death prediction** | Overall mortality = 21.3% | Model outputs ~65% for high-risk profiles | ❌ **Far exceeds** paper rate — likely overfitting noise |

### 3. MDR-TB Subgroup Warning

The paper reports only **17 MDR-TB patients out of 183 (9.3%)**. The vast majority had RR-TB (164 cases, 89.6%). Any model predictions specific to the MDR-TB subgroup are based on a very small sample and should be treated as **statistically unstable**.

### 4. Subgroup Validation Check

To verify whether the 65% death prediction is justified, run the following in the Colab notebook:

```python
kabwe_profile = df[
    (df["district"] == "Kabwe") &
    (df["age_group"] == "Above45") &
    (df["gender"] == "Female") &
    (df["registration_group"] == "New") &
    (df["drtb_type"] == "MDR-TB") &
    (df["hiv_status"] == "Positive")
]
print(kabwe_profile["outcome"].value_counts(normalize=True) * 100)
```

If this subgroup has fewer than 5 records, the prediction is driven by **overfitting noise**, not a real clinical pattern.

### 5. Overall Verdict

> **The model is directionally plausible but over-amplifies Kabwe, HIV, and female gender.** It can be used as an exploratory prototype output for pipeline demonstration, but it must not be presented as evidence that any patient subgroup has a true 65% death risk until validated on real correlated patient data.

| Category | Assessment |
| :--- | :--- |
| **Structural validity** | ✅ Dataset counts match the paper |
| **Directional alignment** | ✅ Death, Kabwe burden, HIV prevalence are correct |
| **Adjusted regression alignment** | ❌ Kabwe, HIV, and gender direction are overclaimed |
| **Calibration** | ❌ 65% >> 21.3% overall mortality |
| **Clinical deployment readiness** | ❌ Not ready — requires real patient data |
