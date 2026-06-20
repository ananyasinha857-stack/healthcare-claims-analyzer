# 🏥 Healthcare Claims Pattern Explorer

A data analytics dashboard analyzing US insurance claim patterns across 6 payers, 11 procedure codes, and 8 medical specialties (2022–2024).

---

## 📊 What it analyzes

- **Denial rates** by payer, procedure, specialty, and US state
- **Denial reasons** — what's actually causing rejections
- **Reimbursement patterns** — what % of charged amount gets paid, and by whom
- **Processing speed** — avg days to payment per payer
- **Charge vs paid gap** — the revenue leakage problem in healthcare billing
- **Monthly trends** — denial rate fluctuation over time
- **US state maps** — geographic claim volume and denial distribution

---

## 💡 Key findings

- **Cigna** has the highest denial rate (~20%) — nearly double Medicare (~8%). Prior auth workflows matter most when billing Cigna
- **"Not medically necessary"** is the top denial reason at ~28% — a documentation problem, not a clinical one. Fixable with better intake checklists
- **Psychiatry and Emergency Medicine** face the steepest denial rates across all specialties — consistent with real-world insurance coverage gaps
- **$3M+ gap** between total charged and total paid across 4,000 claims — illustrating why revenue cycle management is a massive industry
- **Medicare** pays fastest (avg 14 days) and denies least — highest-quality payer from a provider's perspective
- **Knee Replacement (27447)** and **MRI Brain (70553)** have 20–25% denial rates — high-cost procedures get more scrutiny

---

## 🛠️ Tech stack

| Layer | Tools |
|---|---|
| Data generation | Python, NumPy, Pandas |
| Analysis | Pandas, NumPy |
| Visualization | Plotly (choropleth maps, heatmaps, dual-axis charts) |
| Dashboard | Streamlit |

---

## 🚀 How to run

```bash
# 1. Clone the repo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the dataset
python data/generate_data.py

# 4. Launch the dashboard
streamlit run dashboard.py
```

Opens at `http://localhost:8501`

---
## 📌 Data note

The dataset is synthetically generated based on CMS public claims benchmarks and industry denial rate reports. Real US claims data is publicly available via [CMS.gov](https://www.cms.gov/data-research/statistics-trends-and-reports) and can be substituted directly into `data/claims.csv` with the same column schema.
