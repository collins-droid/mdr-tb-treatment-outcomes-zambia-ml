
import pandas as pd
from scipy.stats import chi2_contingency

df = pd.read_csv("drtb_central_zambia_reconstructed_mock.csv")
df['poor_outcome'] = df['outcome'].apply(lambda x: 1 if x in ['Died', 'Lost to Follow Up'] else 0)

# Chi-square for HIV
contingency = pd.crosstab(df['hiv_status'], df['poor_outcome'])
chi2, p, dof, expected = chi2_contingency(contingency)
print(f"HIV Chi-square p-value: {p:.4f}")

# Age mean comparison
poor = df[df['poor_outcome'] == 1]['age_years']
success = df[df['poor_outcome'] == 0]['age_years']
from scipy.stats import ttest_ind
t_stat, t_p = ttest_ind(poor, success)
print(f"Age T-test p-value: {t_p:.4f}")
