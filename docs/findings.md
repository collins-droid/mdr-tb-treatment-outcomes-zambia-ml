# Phase 3: Model Evaluation & Transition to Random Forest

## Objective
The goal of this phase was to replace the baseline Logistic Regression model with a tree-based ensemble method (`RandomForestClassifier`) to see if non-linear interactions could better capture mortality risk predictors, and to formalize evaluation metrics (F1-score, ROC-AUC) beyond simple accuracy.

## Findings: Random Forest vs Logistic Regression

### 1. Updated Model Performance
After switching the pipeline to use `RandomForestClassifier` (100 estimators), the model performance metrics on the test set (46 rows) are as follows:
- **Accuracy**: 54.3% (down from 60.8% with the unweighted Logistic Regression)
- **Macro F1-Score**: 0.211
- **ROC-AUC (OVR)**: 0.594

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

## Phase 4: Statistical Audit Findings (Colab Analysis)

We performed a comprehensive statistical audit following Lecture 4 & 5 standards to validate the reconstructed dataset's clinical utility.

### 1. Descriptive Insights
- **Population Profile**: The dataset correctly reflects the Central Province profile with a mean age of ~35.2 years and a male predominance (57.9%).
- **Outcome Distribution**: The 21.3% mortality rate matches the paper's reported aggregate statistics.

### 2. Inferential Testing (The "Signal Loss" Discovery)
- **HIV vs Outcome**: Chi-square testing returned a p-value of **0.4435**, indicating no statistically significant association between HIV status and treatment outcome in the current dataset.
- **Age vs Outcome**: Independent T-tests returned a p-value of **0.8671**, indicating no significant difference in mean age between success and poor outcome groups.
- **Conclusion**: These results confirm that while the dataset matches *marginal* counts (total deaths, total HIV+), it lacks the *conditional* correlations present in real patient records (e.g., the known clinical link between HIV and mortality). This provides a clear statistical "red flag" that the model's predictions on this mock data should not be used for clinical inference.

### 3. Feature Importance (Random Forest)
- The Random Forest model defaults to **Gender** and **Age Group** as primary predictors because these were the only variables explicitly constrained to mortality in the reconstruction logic.
- Other variables (District, HIV Status) appear as low-importance "noise" in the current model state.

