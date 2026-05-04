"""
Structured DR-TB Mock Dataset Generator
Based on: Chanda, E. (2024). "The clinical profile and outcomes of drug resistant 
tuberculosis in Central Province of Zambia." BMC Infectious Diseases, 24:364.
https://doi.org/10.1186/s12879-024-09238-8

This generator reconstructs a patient-level mock table from published aggregate
counts. It is useful for UI demos, teaching, and pipeline smoke tests.

It is not independent synthetic data, and it cannot reproduce, validate, or
extend the original research. Most inter-variable relationships are unknown
from the publication and are therefore implicitly created by shuffling.

Author: Structured mock data reconstruction for CSC8701 Project
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# SEED FOR REPRODUCIBILITY
# ─────────────────────────────────────────────────────────────────────────────
RANDOM_SEED = 8701
rng = np.random.default_rng(RANDOM_SEED)

# ─────────────────────────────────────────────────────────────────────────────
# PAPER CONSTANTS (Table 1–6 + text)
# ─────────────────────────────────────────────────────────────────────────────

N_TOTAL = 183  # Total DR-TB patients (2017–2021)

# ── Gender ───────────────────────────────────────────────────────────────────
# 106 male (57.9%), 77 female (42.1%)
GENDER_PROBS = {"Male": 106/183, "Female": 77/183}

# ── Age groups (Table 1) ─────────────────────────────────────────────────────
# Counts: 0-15:6, 16-25:29, 26-35:58, 36-45:59, >45:31
AGE_GROUP_COUNTS = {
    "0-15":   {"total": 6,  "male": 3,  "female": 3},
    "16-25":  {"total": 29, "male": 11, "female": 18},
    "26-35":  {"total": 58, "male": 34, "female": 24},
    "36-45":  {"total": 59, "male": 34, "female": 25},
    "Above45":{"total": 31, "male": 24, "female": 7},
}

# Age group → continuous age distribution (mean ± sd per group, truncated)
AGE_CONTINUOUS = {
    "0-15":    (8,  4,   0,  15),
    "16-25":   (21, 3,  16,  25),
    "26-35":   (31, 3,  26,  35),
    "36-45":   (41, 3,  36,  45),
    "Above45": (54, 8,  46,  84),
}
# Paper: mean age 35.24, SD 11.83 → validated below

# ── District (Table 2) ───────────────────────────────────────────────────────
DISTRICT_COUNTS = {
    "Kabwe":         111,
    "Kapiri Mposhi":  19,
    "Chibombo":       12,
    "Chisamba":       10,
    "Mumbwa":          7,
    "Mkushi":          7,
    "Serenje":         4,
    "Chitambo":        2,
    "Other":          11,
}

# ── Year of diagnosis (Fig. 1) ───────────────────────────────────────────────
YEAR_COUNTS = {2017: 27, 2018: 51, 2019: 34, 2020: 36, 2021: 35}

# ── Registration group (Table 3) ─────────────────────────────────────────────
REG_GROUP_COUNTS = {
    "New":                81,
    "Relapse":            90,
    "After loss to FU":    2,
    "Transfer in":         3,
    "Other":               7,
}

# ── HIV status (Table 3) ─────────────────────────────────────────────────────
HIV_COUNTS = {"Positive": 111, "Negative": 61, "Unknown": 11}

# HIV × Registration group cross-table (Table 3)
# Format: (reg_group, hiv_status): count
HIV_REG_CROSSTAB = {
    ("New",               "Positive"): 50, ("New",               "Negative"): 27, ("New",               "Unknown"): 4,
    ("Relapse",           "Positive"): 53, ("Relapse",           "Negative"): 31, ("Relapse",           "Unknown"): 6,
    ("After loss to FU",  "Positive"):  1, ("After loss to FU",  "Negative"):  1, ("After loss to FU",  "Unknown"): 0,
    ("Transfer in",       "Positive"):  2, ("Transfer in",       "Negative"):  0, ("Transfer in",       "Unknown"): 1,
    ("Other",             "Positive"):  5, ("Other",             "Negative"):  2, ("Other",             "Unknown"): 0,
}

# ── Type of DR-TB (Table 4) ───────────────────────────────────────────────────
DRTB_TYPE_COUNTS = {"RR-TB": 164, "MDR-TB": 17, "IR-TB": 1, "XDR-TB": 1}

# DR-TB type × Registration group cross-table (Table 4)
DRTB_REG_CROSSTAB = {
    ("New",               "RR-TB"): 76, ("New",               "IR-TB"): 0, ("New",               "MDR-TB"): 5,  ("New",               "XDR-TB"): 0,
    ("Relapse",           "RR-TB"): 80, ("Relapse",           "IR-TB"): 1, ("Relapse",           "MDR-TB"): 9,  ("Relapse",           "XDR-TB"): 0,
    ("After loss to FU",  "RR-TB"):  1, ("After loss to FU",  "IR-TB"): 0, ("After loss to FU",  "MDR-TB"): 0,  ("After loss to FU",  "XDR-TB"): 1,
    ("Transfer in",       "RR-TB"):  1, ("Transfer in",       "IR-TB"): 0, ("Transfer in",       "MDR-TB"): 2,  ("Transfer in",       "XDR-TB"): 0,
    ("Other",             "RR-TB"):  6, ("Other",             "IR-TB"): 0, ("Other",             "MDR-TB"): 1,  ("Other",             "XDR-TB"): 0,
}

# ── Site of DR-TB ─────────────────────────────────────────────────────────────
# Paper: only 1 extrapulmonary case among 183. Rest = pulmonary.
SITE_COUNTS = {"Pulmonary": 182, "Extrapulmonary": 1}

# ── Treatment outcomes (Table 5) ─────────────────────────────────────────────
# 2021 cases are "Still on Treatment" (SoT) for cured/completed
# Actual outcome counts excluding SoT column (18 SoT patients)
# Cured: M=19, F=12 → total 31 (16.9%)
# Completed: M=51, F=33 → total 84 (45.9%)
# Lost to FU: M=10, F=1 → total 11 but paper says 6% = ~11... 
#   Paper text says "6% defaulted" → 6% of 183 = 10.98 ≈ 11, confirmed by Table 5
# Died: M=16, F=23 → total 39 (21.3%)
# Still on Treatment: 18. Outcomes for patients diagnosed in 2021 were not fully
# evaluated in the paper because patients were still on treatment; any row-level
# outcome assignment for 2021 beyond the published counts is a mock-data
# allocation, not a recovered observation.
OUTCOME_COUNTS = {
    "Cured":              {"Male": 19, "Female": 12, "total": 31},
    "Treatment Completed":{"Male": 51, "Female": 33, "total": 84},
    "Lost to Follow Up":  {"Male": 10, "Female":  1, "total": 11},
    "Died":               {"Male": 16, "Female": 23, "total": 39},
    "Still on Treatment": {"Male":  9, "Female":  9, "total": 18},  # 2021 cohort
}

# Year × outcome distribution (Table 5, plus SoT for 2021)
YEAR_OUTCOME = {
    # (year, outcome): count
    (2017, "Cured"): 4,   (2017, "Treatment Completed"):  9, (2017, "Lost to Follow Up"): 3,  (2017, "Died"): 14,
    (2018, "Cured"): 13,  (2018, "Treatment Completed"): 37, (2018, "Lost to Follow Up"): 4,  (2018, "Died"):  9,
    (2019, "Cured"): 11,  (2019, "Treatment Completed"): 23, (2019, "Lost to Follow Up"): 1,  (2019, "Died"):  8,
    (2020, "Cured"):  3,  (2020, "Treatment Completed"): 15, (2020, "Lost to Follow Up"): 0,  (2020, "Died"):  3,
    (2021, "Still on Treatment"): 18, (2021, "Lost to Follow Up"): 3, (2021, "Died"): 5,
    # Note: 2017: total=30 but only 27 diagnosed → 3 from prior cohort finishing
    #       Paper table 5 N=165 for outcomes + 18 SoT = 183 ✓
}

# ── Mortality risk factors (Table 6) ─────────────────────────────────────────
# Multivariate significant:
#   Age 36-45 vs >45: aOR=0.253 (0.070–0.908), p=0.035  → 36-45 LESS likely to die vs >45 ref
#   Male vs Female:   aOR=0.261 (0.107–0.638), p=0.003  → Male LESS likely to die vs Female ref
# NOTE: aOR < 1 because reference category has higher mortality
#   Female gender and >45 age are higher-risk for death
# Bivariate only significant:
#   Male: OR=0.417 (p=0.018), HIV Negative: OR=0.208 (p=0.026)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Build patient skeleton using exact marginal counts
# ─────────────────────────────────────────────────────────────────────────────

def assign_age_groups():
    """
    Assign age groups respecting gender-stratified counts from Table 1.
    Returns list of (age_group, gender) tuples of length 183.
    """
    records = []
    for age_group, counts in AGE_GROUP_COUNTS.items():
        for _ in range(counts["male"]):
            records.append({"age_group": age_group, "gender": "Male"})
        for _ in range(counts["female"]):
            records.append({"age_group": age_group, "gender": "Female"})
    # Shuffle
    idx = rng.permutation(len(records))
    return [records[i] for i in idx]

def assign_district(n=183):
    """Assign districts by exact counts from Table 2."""
    districts = []
    for dist, count in DISTRICT_COUNTS.items():
        districts.extend([dist] * count)
    rng.shuffle(districts)
    return districts

def assign_year(n=183):
    """Assign year of diagnosis by exact counts from Fig. 1."""
    years = []
    for yr, count in YEAR_COUNTS.items():
        years.extend([yr] * count)
    rng.shuffle(years)
    return years

def assign_reg_group_hiv():
    """
    Assign registration group and HIV status respecting the 
    joint cross-tabulation from Table 3.
    Returns list of (reg_group, hiv_status) tuples.
    """
    records = []
    for (reg, hiv), count in HIV_REG_CROSSTAB.items():
        for _ in range(count):
            records.append({"registration_group": reg, "hiv_status": hiv})
    idx = rng.permutation(len(records))
    return [records[i] for i in idx]

def assign_drtb_type_reg():
    """
    Assign DR-TB type respecting the registration group × type cross-tab (Table 4).
    Returns a list of (drtb_type) values in order matching reg group assignment.
    We need to align this with the registration groups already assigned.
    """
    # Build flat list indexed by registration group
    type_by_reg = {}
    for (reg, drtb), count in DRTB_REG_CROSSTAB.items():
        if reg not in type_by_reg:
            type_by_reg[reg] = []
        type_by_reg[reg].extend([drtb] * count)
    # Shuffle within each group
    for reg in type_by_reg:
        arr = type_by_reg[reg]
        idx = rng.permutation(len(arr))
        type_by_reg[reg] = [arr[i] for i in idx]
    return type_by_reg

def assign_site(n=183):
    """Only 1 extrapulmonary case."""
    sites = ["Pulmonary"] * 182 + ["Extrapulmonary"]
    rng.shuffle(sites)
    return sites

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Assign outcomes with year + gender constraints
# ─────────────────────────────────────────────────────────────────────────────

def assign_outcomes_with_gender(year_list, gender_list):
    """
    Assign treatment outcomes using exact marginal totals from the paper:
      Cured: 31, Treatment Completed: 84, Lost to FU: 11, Died: 39, SoT: 18
    Total = 183 ✓
    
    Important limitation:
    The paper reports that 2021 treatment outcomes were not fully evaluated.
    This function preserves the published marginal totals for demonstration
    purposes, but row-level 2021 outcomes should be treated as mock allocation.
    
    Strategy:
    1. All 35 year-2021 patients get outcomes from {SoT:18, LostFU:3, Died:5} → exact 26,
       but year_counts[2021]=35. Remaining 9 are assigned randomly from 2021 remaining pool.
       Actually Table 5 shows 2021 total = 8 observed + 18 SoT but year count is 35.
       So 35 - 18(SoT) = 17 have outcomes; but Table 5 2021 row: LTF=3, Died=5, SoT=18 → 26
       Remaining 9 from 2021 cohort either had outcomes tracked across years or are still SoT.
       Resolution: Paper says 18 SoT; 35-18=17; 8 had outcomes (3 LTF + 5 died); 9 unresolved.
       We treat all unresolved 2021 patients as SoT (data not yet available).
       
    2. Years 2017-2020: assign remaining outcome pool.
    """
    n = len(year_list)
    outcomes = [None] * n
    
    # Exact totals from paper
    outcome_pool = (
        ["Cured"] * 31 +
        ["Treatment Completed"] * 84 +
        ["Lost to Follow Up"] * 11 +
        ["Died"] * 39 +
        ["Still on Treatment"] * 18
    )
    assert len(outcome_pool) == 183
    
    # Split indices by year
    indices_2021 = [i for i, yr in enumerate(year_list) if yr == 2021]  # 35 patients
    indices_other = [i for i, yr in enumerate(year_list) if yr != 2021]  # 148 patients
    
    # Global pool: Cured=31, Completed=84, LTF=11, Died=39, SoT=18 → 183
    # 2021 patients must use ALL 18 SoT + 3 LTF + 5 Died = 26 confirmed outcomes
    # The remaining 9 (35-26=9) draw from the non-SoT pool shared with 2017-2020
    # Non-SoT pool: Cured=31, Completed=84, LTF=8, Died=34 = 157
    # 157 must fill: 148 (other years) + 9 (2021 remainder) = 157 ✓
    
    non_sot_pool = (
        ["Cured"] * 31 +
        ["Treatment Completed"] * 84 +
        ["Lost to Follow Up"] * 8 +   # 11 - 3 reserved for 2021
        ["Died"] * 34                  # 39 - 5 reserved for 2021
    )
    assert len(non_sot_pool) == 157
    
    # Assign 2021 patients
    pool_2021_fixed = ["Still on Treatment"] * 18 + ["Lost to Follow Up"] * 3 + ["Died"] * 5
    # 9 more 2021 patients draw from non_sot_pool
    arr_2021_fixed = list(pool_2021_fixed)
    
    non_sot_list = list(non_sot_pool)
    rng.shuffle(non_sot_list)
    
    # Take 9 outcomes from non_sot for 2021
    pool_2021_extra = non_sot_list[:9]
    non_sot_remaining = non_sot_list[9:]  # 148 for other years
    
    full_2021_pool = arr_2021_fixed + pool_2021_extra  # 26 + 9 = 35
    assert len(full_2021_pool) == 35
    rng.shuffle(full_2021_pool)
    for i, outcome in zip(indices_2021, full_2021_pool):
        outcomes[i] = outcome
    
    # Assign 2017-2020 patients
    assert len(non_sot_remaining) == len(indices_other), \
        f"Pool size {len(non_sot_remaining)} != {len(indices_other)}"
    rng.shuffle(non_sot_remaining)
    for i, outcome in zip(indices_other, non_sot_remaining):
        outcomes[i] = outcome
    
    return outcomes

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Generate continuous age from age group
# ─────────────────────────────────────────────────────────────────────────────

def generate_continuous_age(age_group):
    mean, sd, lo, hi = AGE_CONTINUOUS[age_group]
    # Draw from truncated normal
    for _ in range(1000):
        age = rng.normal(mean, sd)
        if lo <= age <= hi:
            return round(float(age), 1)
    return float(mean)  # fallback

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Add realistic mortality-aligned noise
# ─────────────────────────────────────────────────────────────────────────────

def adjust_outcome_gender_mortality(df):
    """
    Post-process to nudge the Died outcome toward female patients,
    consistent with the paper's multivariate finding (female reference
    category has higher risk: aOR for male = 0.261, p=0.003).
    
    Paper: 16 Male deaths, 23 Female deaths (Table 5).
    We swap outcomes within the 'Died' pool to match these exact counts.
    """
    died_indices = df.index[df['outcome'] == 'Died'].tolist()
    male_died = df.loc[died_indices, 'gender'] == 'Male'
    n_male_died = male_died.sum()
    n_female_died = (~male_died).sum()
    
    target_male_died = 16
    target_female_died = 23
    
    if n_male_died == target_male_died:
        return df  # Already correct
    
    # Indices of non-died patients for possible swap
    non_died_indices = df.index[~df['outcome'].isin(['Died'])].tolist()
    
    if n_male_died > target_male_died:
        # Too many male deaths: swap some male Died → female Died
        excess_male_died_idx = [i for i in died_indices if df.at[i, 'gender'] == 'Male']
        female_non_died_idx = [i for i in non_died_indices if df.at[i, 'gender'] == 'Female']
        n_swap = n_male_died - target_male_died
        for k in range(min(n_swap, len(excess_male_died_idx), len(female_non_died_idx))):
            # Swap outcomes between a male Died and a female non-Died
            m_idx = excess_male_died_idx[k]
            f_idx = female_non_died_idx[k]
            # Give the male patient the female's outcome and vice versa for Died
            df.at[m_idx, 'outcome'], df.at[f_idx, 'outcome'] = df.at[f_idx, 'outcome'], 'Died'
    else:
        # Too few male deaths: swap female Died → male Died
        excess_female_died_idx = [i for i in died_indices if df.at[i, 'gender'] == 'Female']
        male_non_died_idx = [i for i in non_died_indices if df.at[i, 'gender'] == 'Male']
        n_swap = target_male_died - n_male_died
        for k in range(min(n_swap, len(excess_female_died_idx), len(male_non_died_idx))):
            f_idx = excess_female_died_idx[k]
            m_idx = male_non_died_idx[k]
            df.at[f_idx, 'outcome'], df.at[m_idx, 'outcome'] = df.at[m_idx, 'outcome'], 'Died'
    
    return df

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Main generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_dataset():
    print("=" * 65)
    print("  DR-TB Structured Mock Dataset Generator")
    print("  Based on: Chanda BMC Infect Dis (2024) 24:364")
    print("=" * 65)
    
    # --- Age group + gender (Table 1) ---
    age_gender_records = assign_age_groups()
    age_groups = [r["age_group"] for r in age_gender_records]
    genders = [r["gender"] for r in age_gender_records]
    
    # --- Continuous age ---
    ages = [generate_continuous_age(ag) for ag in age_groups]
    
    # --- District (Table 2) ---
    districts = assign_district()
    
    # --- Year (Fig. 1) ---
    years = assign_year()
    
    # --- Registration group + HIV (Table 3) ---
    reg_hiv_records = assign_reg_hiv = assign_reg_group_hiv()
    reg_groups = [r["registration_group"] for r in reg_hiv_records]
    hiv_statuses = [r["hiv_status"] for r in reg_hiv_records]
    
    # --- DR-TB type aligned with registration group (Table 4) ---
    type_by_reg = assign_drtb_type_reg()
    reg_group_counters = {reg: 0 for reg in REG_GROUP_COUNTS}
    drtb_types = []
    for reg in reg_groups:
        idx = reg_group_counters[reg]
        pool = type_by_reg[reg]
        drtb_types.append(pool[idx])
        reg_group_counters[reg] += 1
    
    # --- Site ---
    sites = assign_site()
    
    # --- Outcomes (year-constrained, Table 5) ---
    outcomes = assign_outcomes_with_gender(years, genders)
    
    # ── Assemble DataFrame ──────────────────────────────────────────────────
    df = pd.DataFrame({
        "patient_id":         [f"DRTB-{i+1:04d}" for i in range(N_TOTAL)],
        "year_of_diagnosis":  years,
        "age_years":          ages,
        "age_group":          age_groups,
        "gender":             genders,
        "district":           districts,
        "registration_group": reg_groups,
        "hiv_status":         hiv_statuses,
        "site_of_drtb":       sites,
        "drtb_type":          drtb_types,
        "outcome":            outcomes,
    })
    
    # ── Post-process: align died counts with gender (Table 5) ───────────────
    df = adjust_outcome_gender_mortality(df)
    
    # ── Add binary / derived columns ────────────────────────────────────────
    df["died"] = (df["outcome"] == "Died").astype(int)
    df["treatment_success"] = df["outcome"].isin(
        ["Cured", "Treatment Completed"]
    ).astype(int)
    df["lost_to_followup"] = (df["outcome"] == "Lost to Follow Up").astype(int)
    
    # Age numeric group for regression
    age_group_map = {"0-15": 1, "16-25": 2, "26-35": 3, "36-45": 4, "Above45": 5}
    df["age_group_code"] = df["age_group"].map(age_group_map)
    
    # Male dummy
    df["is_male"] = (df["gender"] == "Male").astype(int)
    
    # HIV positive dummy
    df["hiv_positive"] = (df["hiv_status"] == "Positive").astype(int)
    
    return df

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Validation against paper
# ─────────────────────────────────────────────────────────────────────────────

def validate_dataset(df):
    print("\n" + "─" * 65)
    print("  VALIDATION AGAINST PUBLISHED AGGREGATE COUNTS")
    print("─" * 65)
    
    passed = 0
    failed = 0
    
    def check(label, actual, expected, tol=0.015):
        nonlocal passed, failed
        ok = abs(actual - expected) <= tol
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  {status}  {label}")
        print(f"         Expected: {expected:.4f}  |  Got: {actual:.4f}  |  Δ={abs(actual-expected):.4f}")
    
    n = len(df)
    
    # 1. Total N
    assert n == 183, f"N must be 183, got {n}"
    print(f"\n  ✓ PASS  Total N = {n} (expected 183)")
    passed += 1
    
    # 2. Gender
    p_male = (df['gender'] == 'Male').mean()
    check("Male prevalence (57.9%)", p_male, 106/183)
    
    # 3. Age groups
    print("\n  Age group proportions:")
    expected_ag = {"0-15": 6/183, "16-25": 29/183, "26-35": 58/183,
                   "36-45": 59/183, "Above45": 31/183}
    for ag, exp in expected_ag.items():
        actual = (df['age_group'] == ag).mean()
        check(f"  Age {ag} ({exp*100:.1f}%)", actual, exp)
    
    # 4. Mean age
    mean_age = df['age_years'].mean()
    check("Mean age (paper: 35.24)", mean_age/35.24, 1.0, tol=0.05)
    print(f"         (Actual mean: {mean_age:.2f}, SD: {df['age_years'].std():.2f})")
    
    # 5. Districts
    print("\n  District distribution:")
    for dist, cnt in DISTRICT_COUNTS.items():
        actual = (df['district'] == dist).sum()
        ok = actual == cnt
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status}  {dist}: expected {cnt}, got {actual}")
    
    # 6. Year
    print("\n  Year of diagnosis:")
    for yr, cnt in YEAR_COUNTS.items():
        actual = (df['year_of_diagnosis'] == yr).sum()
        ok = actual == cnt
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status}  {yr}: expected {cnt}, got {actual}")
    
    # 7. Registration group
    print("\n  Registration group:")
    for rg, cnt in REG_GROUP_COUNTS.items():
        actual = (df['registration_group'] == rg).sum()
        ok = actual == cnt
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status}  {rg}: expected {cnt}, got {actual}")
    
    # 8. HIV status
    print("\n  HIV status:")
    for hiv, cnt in HIV_COUNTS.items():
        actual = (df['hiv_status'] == hiv).sum()
        ok = actual == cnt
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status}  {hiv}: expected {cnt}, got {actual}")
    
    # 9. DR-TB type
    print("\n  DR-TB type:")
    for t, cnt in DRTB_TYPE_COUNTS.items():
        actual = (df['drtb_type'] == t).sum()
        ok = actual == cnt
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status}  {t}: expected {cnt}, got {actual}")
    
    # 10. Outcomes
    print("\n  Treatment outcomes:")
    outcome_expected = {
        "Cured": 31, "Treatment Completed": 84,
        "Lost to Follow Up": 11, "Died": 39, "Still on Treatment": 18
    }
    for oc, cnt in outcome_expected.items():
        actual = (df['outcome'] == oc).sum()
        ok = actual == cnt
        status = "✓ PASS" if ok else "✗ FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  {status}  {oc}: expected {cnt}, got {actual}")
    
    # 11. Mortality rate
    p_died = df['died'].mean()
    check("Mortality rate (21.3%)", p_died, 39/183)
    
    # 12. Completion rate (paper: 45.9%)
    p_complete = (df['outcome'] == 'Treatment Completed').mean()
    check("Treatment completion rate (45.9%)", p_complete, 84/183)
    
    # 13. Lost to FU rate (paper: 6%)
    p_ltfu = (df['outcome'] == 'Lost to Follow Up').mean()
    check("Lost to follow-up rate (6.0%)", p_ltfu, 11/183)
    
    # 14. Gender × Died (Table 5: M=16, F=23)
    male_deaths = df[df['gender'] == 'Male']['died'].sum()
    female_deaths = df[df['gender'] == 'Female']['died'].sum()
    ok_m = male_deaths == 16
    ok_f = female_deaths == 23
    print(f"\n  {'✓ PASS' if ok_m else '✗ FAIL'}  Male deaths: expected 16, got {male_deaths}")
    print(f"  {'✓ PASS' if ok_f else '✗ FAIL'}  Female deaths: expected 23, got {female_deaths}")
    if ok_m: passed += 1
    else: failed += 1
    if ok_f: passed += 1
    else: failed += 1
    
    # 15. RR-TB in new cases (93.8%) and relapse (88.9%)
    new_cases = df[df['registration_group'] == 'New']
    relapse_cases = df[df['registration_group'] == 'Relapse']
    rr_new = (new_cases['drtb_type'] == 'RR-TB').mean()
    rr_relapse = (relapse_cases['drtb_type'] == 'RR-TB').mean()
    check("RR-TB in new cases (93.8%)", rr_new, 76/81)
    check("RR-TB in relapse cases (88.9%)", rr_relapse, 80/90)
    
    # 16. HIV positive in new cases (61.7%)
    hiv_new = (new_cases['hiv_status'] == 'Positive').mean()
    check("HIV+ in new cases (61.7%)", hiv_new, 50/81)
    
    # 17. HIV positive in relapse (58.9%)
    hiv_relapse = (relapse_cases['hiv_status'] == 'Positive').mean()
    check("HIV+ in relapse cases (58.9%)", hiv_relapse, 53/90)
    
    # 18. Kabwe district predominance (60.7%)
    kabwe_pct = (df['district'] == 'Kabwe').mean()
    check("Kabwe district proportion (60.7%)", kabwe_pct, 111/183)
    
    # 19. Extrapulmonary = 1
    n_extra = (df['site_of_drtb'] == 'Extrapulmonary').sum()
    ok = n_extra == 1
    status = "✓ PASS" if ok else "✗ FAIL"
    if ok: passed += 1
    else: failed += 1
    print(f"\n  {status}  Extrapulmonary cases: expected 1, got {n_extra}")
    
    # ── Summary ─────────────────────────────────────────────────────────────
    print("\n" + "─" * 65)
    total = passed + failed
    print(f"  RESULT: {passed}/{total} checks passed")
    if failed == 0:
        print("  ✓ ALL CHECKS PASSED — Mock table matches selected published aggregate counts")
    else:
        print(f"  ✗ {failed} check(s) failed — review output above")
    print("─" * 65)
    
    return passed, failed

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: Summary statistics table
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(df):
    print("\n" + "=" * 65)
    print("  DATASET SUMMARY")
    print("=" * 65)
    print(f"\n  Total patients: {len(df)}")
    print(f"  Study period:   2017–2021 (Central Province, Zambia)")
    print(f"  Source:         Kabwe Central Hospital MDR-TB Ward")
    print(f"  Mean age:       {df['age_years'].mean():.2f} years (SD={df['age_years'].std():.2f})")
    print(f"  Age range:      {df['age_years'].min():.1f} – {df['age_years'].max():.1f} years")
    
    print(f"\n  Gender:")
    print(df['gender'].value_counts().to_string())
    
    print(f"\n  DR-TB Type:")
    print(df['drtb_type'].value_counts().to_string())
    
    print(f"\n  Treatment Outcomes:")
    print(df['outcome'].value_counts().to_string())
    
    print(f"\n  HIV Status:")
    print(df['hiv_status'].value_counts().to_string())
    
    print(f"\n  Top 5 Districts:")
    print(df['district'].value_counts().head(5).to_string())

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = generate_dataset()
    passed, failed = validate_dataset(df)
    print_summary(df)
    
    # ── Save outputs ─────────────────────────────────────────────────────────
    output_csv = "drtb_central_zambia_reconstructed_mock.csv"
    output_excel = "drtb_central_zambia_reconstructed_mock.xlsx"
    
    df.to_csv(output_csv, index=False)
    df.to_excel(output_excel, index=False)
    
    print(f"\n  Files saved:")
    print(f"    → {output_csv}")
    print(f"    → {output_excel}")
    print("\n" + "=" * 65)
    print("  COLUMN REFERENCE")
    print("=" * 65)
    cols_desc = {
        "patient_id":           "Unique patient identifier (DRTB-0001 ... DRTB-0183)",
        "year_of_diagnosis":    "Year DR-TB diagnosed (2017–2021)",
        "age_years":            "Continuous age (years); mean≈35.24, SD≈11.83",
        "age_group":            "Grouped age (0-15 / 16-25 / 26-35 / 36-45 / Above45)",
        "gender":               "Male / Female",
        "district":             "District within Central Province",
        "registration_group":   "New / Relapse / After loss to FU / Transfer in / Other",
        "hiv_status":           "Positive / Negative / Unknown",
        "site_of_drtb":         "Pulmonary / Extrapulmonary",
        "drtb_type":            "RR-TB / MDR-TB / IR-TB / XDR-TB",
        "outcome":              "Cured / Treatment Completed / Lost to Follow Up / Died / Still on Treatment",
        "died":                 "Binary: 1=Died, 0=otherwise",
        "treatment_success":    "Binary: 1=Cured or Completed, 0=otherwise",
        "lost_to_followup":     "Binary: 1=Lost to FU, 0=otherwise",
        "age_group_code":       "Ordinal code: 1=0-15, 2=16-25, 3=26-35, 4=36-45, 5=Above45",
        "is_male":              "Binary: 1=Male, 0=Female",
        "hiv_positive":         "Binary: 1=HIV+, 0=HIV- or Unknown",
    }
    for col, desc in cols_desc.items():
        print(f"  {col:<25} {desc}")
    print("=" * 65)
