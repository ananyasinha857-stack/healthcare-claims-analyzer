"""
generate_data.py
================
Generates a realistic US healthcare insurance claims dataset (2022–2024).
Run once before launching the dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

PAYERS = {
    "BlueCross BlueShield": {"weight": 0.28, "denial_rate": 0.12, "avg_pay_days": 18},
    "UnitedHealth":         {"weight": 0.22, "denial_rate": 0.18, "avg_pay_days": 22},
    "Aetna":                {"weight": 0.18, "denial_rate": 0.15, "avg_pay_days": 20},
    "Cigna":                {"weight": 0.15, "denial_rate": 0.20, "avg_pay_days": 25},
    "Humana":               {"weight": 0.10, "denial_rate": 0.14, "avg_pay_days": 19},
    "Medicare":             {"weight": 0.07, "denial_rate": 0.08, "avg_pay_days": 14},
}

PROCEDURE_CODES = {
    "99213 - Office Visit (Est.)":      {"weight": 0.20, "avg_charge": 180,  "denial_risk": 0.08},
    "99214 - Office Visit (Complex)":   {"weight": 0.15, "avg_charge": 250,  "denial_risk": 0.10},
    "93000 - ECG":                      {"weight": 0.10, "avg_charge": 120,  "denial_risk": 0.12},
    "71046 - Chest X-Ray":              {"weight": 0.08, "avg_charge": 200,  "denial_risk": 0.15},
    "80053 - Comprehensive Metabolic":  {"weight": 0.10, "avg_charge": 95,   "denial_risk": 0.07},
    "99285 - ER Visit (High):":         {"weight": 0.07, "avg_charge": 1200, "denial_risk": 0.22},
    "27447 - Knee Replacement":         {"weight": 0.04, "avg_charge": 28000,"denial_risk": 0.25},
    "43239 - Upper GI Endoscopy":       {"weight": 0.05, "avg_charge": 3500, "denial_risk": 0.18},
    "70553 - MRI Brain w/ Contrast":    {"weight": 0.06, "avg_charge": 2800, "denial_risk": 0.20},
    "99232 - Subsequent Hospital Care": {"weight": 0.08, "avg_charge": 220,  "denial_risk": 0.09},
    "90837 - Psychotherapy 60 min":     {"weight": 0.07, "avg_charge": 180,  "denial_risk": 0.28},
}

DENIAL_REASONS = [
    "Not medically necessary",
    "Prior authorization required",
    "Out of network provider",
    "Duplicate claim",
    "Missing / invalid diagnosis code",
    "Service not covered",
    "Coordination of benefits issue",
    "Timely filing limit exceeded",
]
DENIAL_REASON_WEIGHTS = [0.28, 0.22, 0.15, 0.10, 0.10, 0.08, 0.04, 0.03]

CLAIM_TYPES = ["837P - Professional", "837I - Institutional", "835 - Remittance"]
CLAIM_TYPE_WEIGHTS = [0.55, 0.30, 0.15]

STATES = ["CA", "TX", "NY", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
          "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"]

SPECIALTIES = ["Primary Care", "Cardiology", "Orthopedics", "Radiology",
               "Emergency Medicine", "Gastroenterology", "Psychiatry", "Neurology"]


def generate_claims(n=4000):
    records = []
    payer_names   = list(PAYERS.keys())
    payer_weights = [PAYERS[p]["weight"] for p in payer_names]
    proc_names    = list(PROCEDURE_CODES.keys())
    proc_weights  = [PROCEDURE_CODES[p]["weight"] for p in proc_names]

    for i in range(n):
        claim_id  = f"CLM-{2022 + i % 3}-{str(i+1).zfill(5)}"
        payer     = random.choices(payer_names, weights=payer_weights)[0]
        procedure = random.choices(proc_names,  weights=proc_weights)[0]

        start = datetime(2022, 1, 1)
        end   = datetime(2024, 12, 31)
        filed = start + timedelta(days=random.randint(0, (end - start).days))

        base_denial  = PAYERS[payer]["denial_rate"]
        proc_risk    = PROCEDURE_CODES[procedure]["denial_risk"]
        denial_prob  = (base_denial + proc_risk) / 2
        is_denied    = random.random() < denial_prob

        denial_reason = (
            random.choices(DENIAL_REASONS, weights=DENIAL_REASON_WEIGHTS)[0]
            if is_denied else None
        )

        avg_charge = PROCEDURE_CODES[procedure]["avg_charge"]
        charge     = round(max(10, np.random.normal(avg_charge, avg_charge * 0.15)), 2)

        allowed_pct = random.uniform(0.55, 0.85)
        allowed     = round(charge * allowed_pct, 2) if not is_denied else 0
        paid        = round(allowed * random.uniform(0.70, 0.95), 2) if not is_denied else 0
        patient_responsibility = round(allowed - paid, 2) if not is_denied else 0

        avg_days = PAYERS[payer]["avg_pay_days"]
        pay_days = max(1, int(np.random.normal(avg_days, avg_days * 0.3)))
        paid_date = filed + timedelta(days=pay_days) if not is_denied else None

        records.append({
            "claim_id":               claim_id,
            "filed_date":             filed.strftime("%Y-%m-%d"),
            "year":                   filed.year,
            "month":                  filed.month,
            "month_name":             filed.strftime("%B"),
            "quarter":                f"Q{(filed.month - 1) // 3 + 1}",
            "payer":                  payer,
            "procedure_code":         procedure,
            "claim_type":             random.choices(CLAIM_TYPES, weights=CLAIM_TYPE_WEIGHTS)[0],
            "specialty":              random.choice(SPECIALTIES),
            "state":                  random.choice(STATES),
            "charge_amount":          charge,
            "allowed_amount":         allowed,
            "paid_amount":            paid,
            "patient_responsibility": patient_responsibility,
            "is_denied":              is_denied,
            "denial_reason":          denial_reason,
            "days_to_payment":        pay_days if not is_denied else None,
            "paid_date":              paid_date.strftime("%Y-%m-%d") if paid_date else None,
            "month_year":             filed.strftime("%Y-%m"),
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df  = generate_claims(4000)
    out = os.path.join(os.path.dirname(__file__), "claims.csv")
    df.to_csv(out, index=False)
    print(f"✓ Generated {len(df)} claim records → {out}")
    print(f"  Total charged : ${df['charge_amount'].sum():,.0f}")
    print(f"  Total paid    : ${df['paid_amount'].sum():,.0f}")
    print(f"  Overall denial: {df['is_denied'].mean()*100:.1f}%")