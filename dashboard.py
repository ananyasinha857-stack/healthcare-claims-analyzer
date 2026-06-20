"""
dashboard.py — Healthcare Claims Pattern Explorer
==================================================
Run with:  streamlit run dashboard.py

Author: Ananya Sinha
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Healthcare Claims Explorer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

FONT = dict(color="black", family="Arial")

PAYER_COLORS = {
    "BlueCross BlueShield": "#003087",
    "UnitedHealth":         "#E05252",
    "Aetna":                "#7B2D8B",
    "Cigna":                "#1D9E75",
    "Humana":               "#EF9F27",
    "Medicare":             "#378ADD",
}

STATUS_COLORS = {
    "Paid":   "#1D9E75",
    "Denied": "#E05252",
}


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "claims.csv")
    df   = pd.read_csv(path, parse_dates=["filed_date", "paid_date"])
    df["status"] = df["is_denied"].map({True: "Denied", False: "Paid"})
    df["reimbursement_rate"] = np.where(
        df["charge_amount"] > 0,
        df["paid_amount"] / df["charge_amount"] * 100, 0
    )
    return df

df_full = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🏥 Filters")
years             = sorted(df_full["year"].unique())
selected_years    = st.sidebar.multiselect("Year", years, default=years)
selected_payers   = st.sidebar.multiselect("Payer", sorted(df_full["payer"].unique()), default=sorted(df_full["payer"].unique()))
selected_types    = st.sidebar.multiselect("Claim Type", sorted(df_full["claim_type"].unique()), default=sorted(df_full["claim_type"].unique()))
selected_specs    = st.sidebar.multiselect("Specialty", sorted(df_full["specialty"].unique()), default=sorted(df_full["specialty"].unique()))

df = df_full[
    df_full["year"].isin(selected_years) &
    df_full["payer"].isin(selected_payers) &
    df_full["claim_type"].isin(selected_types) &
    df_full["specialty"].isin(selected_specs)
].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏥 Healthcare Claims Pattern Explorer")
st.markdown(
    "Analyzing **4,000 insurance claims** across 6 payers, 11 procedure codes, "
    "and 8 specialties (2022–2024). Identifies denial patterns, payer behavior, "
    "and reimbursement trends.  \n"
)
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
total         = len(df)
denial_rate   = df["is_denied"].mean() * 100
total_charged = df["charge_amount"].sum()
total_paid    = df["paid_amount"].sum()
avg_reimb     = df[~df["is_denied"]]["reimbursement_rate"].mean()
avg_pay_days  = df[~df["is_denied"]]["days_to_payment"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Claims",        f"{total:,}")
k2.metric("Overall Denial Rate", f"{denial_rate:.1f}%")
k3.metric("Total Charged",       f"${total_charged:,.0f}")
k4.metric("Total Paid",          f"${total_paid:,.0f}")
k5.metric("Avg Reimbursement",   f"{avg_reimb:.1f}%")
st.markdown("---")

# ── Row 1: Denial rate by payer + Claim volume ────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚫 Denial rate by payer")
    payer_denial = (
        df.groupby("payer")["is_denied"].mean() * 100
    ).reset_index().sort_values("is_denied", ascending=True)
    payer_denial.columns = ["payer", "denial_rate"]

    fig = px.bar(
        payer_denial, x="denial_rate", y="payer", orientation="h",
        color="denial_rate", color_continuous_scale="Reds",
        labels={"denial_rate": "Denial rate (%)", "payer": ""},
        text=payer_denial["denial_rate"].round(1).astype(str) + "%",
    )
    fig.update_traces(textposition="outside", textfont=dict(color="black", size=10))
    fig.update_layout(
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=10, b=10, r=60), height=320,
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black")),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Claim volume by payer & status")
    vol_df = df.groupby(["payer", "status"]).size().reset_index(name="count")
    fig = px.bar(
        vol_df, x="payer", y="count", color="status",
        color_discrete_map=STATUS_COLORS, barmode="stack",
        labels={"payer": "", "count": "Claims", "status": "Status"},
    )
    fig.update_layout(
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(font=dict(color="black", size=10)),
        margin=dict(t=10, b=10), height=320,
        xaxis=dict(tickangle=20, tickfont=dict(color="black", size=9)),
        yaxis=dict(tickfont=dict(color="black")),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Denial reasons + Heatmap ──────────────────────────────────────────
col3, col4 = st.columns([2, 3])

with col3:
    st.subheader("❌ Top denial reasons")
    reasons = df[df["is_denied"]]["denial_reason"].value_counts().reset_index()
    reasons.columns = ["reason", "count"]
    reasons = reasons.sort_values("count")

    fig = px.bar(
        reasons, x="count", y="reason", orientation="h",
        color="count", color_continuous_scale="Oranges",
        labels={"count": "Denied claims", "reason": ""},
        text=reasons["count"],
    )
    fig.update_traces(textposition="outside", textfont=dict(color="black", size=9))
    fig.update_layout(
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=10, b=10, r=40), height=360,
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black", size=9)),
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("🗂️ Denial rate: payer × procedure")
    heat_df = (
        df.groupby(["payer", "procedure_code"])["is_denied"].mean() * 100
    ).reset_index()
    heat_df.columns = ["payer", "procedure", "denial_rate"]
    heat_df["procedure"] = heat_df["procedure"].str.split(" - ").str[0] + " " + \
                           heat_df["procedure"].str.split(" - ").str[1].str[:18]
    pivot = heat_df.pivot(index="payer", columns="procedure", values="denial_rate").fillna(0)

    fig = px.imshow(
        pivot, color_continuous_scale="Reds",
        labels=dict(x="Procedure", y="Payer", color="Denial %"),
        text_auto=".1f", aspect="auto",
    )
    fig.update_traces(textfont=dict(color="black", size=9))
    fig.update_layout(
        font=FONT, paper_bgcolor="white",
        margin=dict(t=10, b=10), height=360,
        xaxis=dict(tickangle=30, tickfont=dict(color="black", size=8)),
        yaxis=dict(tickfont=dict(color="black", size=9)),
        coloraxis_colorbar=dict(tickfont=dict(color="black"), title=dict(font=dict(color="black"))),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Monthly trend ──────────────────────────────────────────────────────
st.subheader("📅 Monthly claims volume & denial rate trend")
monthly = df.groupby("month_year").agg(
    total_claims=("claim_id", "count"),
    denied=("is_denied", "sum"),
).reset_index()
monthly["denial_rate"] = monthly["denied"] / monthly["total_claims"] * 100
monthly = monthly.sort_values("month_year")

fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly["month_year"], y=monthly["total_claims"],
    name="Total Claims", marker_color="#378ADD", opacity=0.8, yaxis="y",
))
fig.add_trace(go.Scatter(
    x=monthly["month_year"], y=monthly["denial_rate"],
    name="Denial Rate %", mode="lines+markers",
    line=dict(color="#E05252", width=2), marker_color="#E05252", yaxis="y2",
))
fig.update_layout(
    font=FONT, plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=10, b=10), height=320,
    legend=dict(font=dict(color="black", size=10)),
    xaxis=dict(tickangle=45, tickfont=dict(color="black", size=8)),
    yaxis=dict(title="Claims", tickfont=dict(color="black")),
    yaxis2=dict(title=dict(text="Denial Rate %", font=dict(color="black")), overlaying="y", side="right",
                tickfont=dict(color="black"),),
)

st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Reimbursement + Days to payment ────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("💰 Avg reimbursement rate by payer")
    reimb_df = (
        df[~df["is_denied"]].groupby("payer")["reimbursement_rate"]
        .mean().reset_index().sort_values("reimbursement_rate", ascending=True)
    )
    reimb_df.columns = ["payer", "avg_reimb"]

    fig = px.bar(
        reimb_df, x="avg_reimb", y="payer", orientation="h",
        color="avg_reimb", color_continuous_scale="Greens",
        labels={"avg_reimb": "Avg reimbursement %", "payer": ""},
        text=reimb_df["avg_reimb"].round(1).astype(str) + "%",
    )
    fig.update_traces(textposition="outside", textfont=dict(color="black", size=10))
    fig.update_layout(
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=10, b=10, r=60), height=320,
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black")),
    )
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("⏱️ Avg days to payment by payer")
    days_df = (
        df[~df["is_denied"]].groupby("payer")["days_to_payment"]
        .mean().reset_index().sort_values("days_to_payment", ascending=True)
    )
    days_df.columns = ["payer", "avg_days"]

    fig = px.bar(
        days_df, x="avg_days", y="payer", orientation="h",
        color="avg_days", color_continuous_scale="Blues",
        labels={"avg_days": "Avg days to payment", "payer": ""},
        text=days_df["avg_days"].round(1),
    )
    fig.update_traces(textposition="outside", textfont=dict(color="black", size=10))
    fig.update_layout(
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=10, b=10, r=60), height=320,
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black")),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Row 5: Procedure billing + Specialty denial ────────────────────────────────
col7, col8 = st.columns(2)

with col7:
    st.subheader("🔬 Avg charge vs paid by procedure")
    proc_df = (
        df.groupby("procedure_code")
        .agg(avg_charge=("charge_amount","mean"), avg_paid=("paid_amount","mean"))
        .reset_index().sort_values("avg_charge", ascending=False)
    )
    proc_df["short"] = proc_df["procedure_code"].str.split(" - ").str[0]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Avg Charge", x=proc_df["short"], y=proc_df["avg_charge"],
        marker_color="#E05252", opacity=0.8,
    ))
    fig.add_trace(go.Bar(
        name="Avg Paid", x=proc_df["short"], y=proc_df["avg_paid"],
        marker_color="#1D9E75", opacity=0.9,
    ))
    fig.update_layout(
        font=FONT, barmode="group",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10, b=10), height=340,
        legend=dict(font=dict(color="black", size=10)),
        xaxis=dict(tickangle=30, tickfont=dict(color="black", size=9)),
        yaxis=dict(tickfont=dict(color="black"), title="Amount ($)"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.subheader("🏥 Denial rate by specialty")
    spec_df = (
        df.groupby("specialty")["is_denied"].mean() * 100
    ).reset_index().sort_values("is_denied", ascending=True)
    spec_df.columns = ["specialty", "denial_rate"]

    fig = px.bar(
        spec_df, x="denial_rate", y="specialty", orientation="h",
        color="denial_rate", color_continuous_scale="RdYlGn_r",
        labels={"denial_rate": "Denial rate (%)", "specialty": ""},
        text=spec_df["denial_rate"].round(1).astype(str) + "%",
    )
    fig.update_traces(textposition="outside", textfont=dict(color="black", size=10))
    fig.update_layout(
        font=FONT, plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=10, b=10, r=60), height=340,
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black")),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Row 6: State maps ─────────────────────────────────────────────────────────
st.subheader("🗺️ Claim volume & denial rate by state")
state_df = df.groupby("state").agg(
    total=("claim_id", "count"),
    denial_rate=("is_denied", lambda x: round(x.mean() * 100, 1)),
    total_paid=("paid_amount", "sum"),
).reset_index()

col9, col10 = st.columns(2)
with col9:
    fig = px.choropleth(
        state_df, locations="state", locationmode="USA-states",
        color="total", scope="usa", color_continuous_scale="Purples",
        labels={"total": "Claims"}, title="Claims by state",
    )
    fig.update_layout(
        font=FONT, paper_bgcolor="white", margin=dict(t=30, b=10), height=320,
        geo=dict(bgcolor="white"),
        coloraxis_colorbar=dict(tickfont=dict(color="black"), title=dict(font=dict(color="black"))),
        title_font=dict(color="black"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col10:
    fig = px.choropleth(
        state_df, locations="state", locationmode="USA-states",
        color="denial_rate", scope="usa", color_continuous_scale="Reds",
        labels={"denial_rate": "Denial %"}, title="Denial rate by state",
    )
    fig.update_layout(
        font=FONT, paper_bgcolor="white", margin=dict(t=30, b=10), height=320,
        geo=dict(bgcolor="white"),
        coloraxis_colorbar=dict(tickfont=dict(color="black"), title=dict(font=dict(color="black"))),
        title_font=dict(color="black"),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💡 Key Insights")

worst_payer    = payer_denial.sort_values("denial_rate", ascending=False).iloc[0]
best_payer     = payer_denial.sort_values("denial_rate").iloc[0]
top_reason     = df[df["is_denied"]]["denial_reason"].value_counts().idxmax()
top_reason_pct = df[df["is_denied"]]["denial_reason"].value_counts(normalize=True).max() * 100
worst_proc     = (df.groupby("procedure_code")["is_denied"].mean() * 100).idxmax()
gap            = total_charged - total_paid

i1, i2, i3 = st.columns(3)
with i1:
    st.error(
        f"**🚨 {worst_payer['payer']}** has the highest denial rate at "
        f"**{worst_payer['denial_rate']:.1f}%** — nearly double {best_payer['payer']} "
        f"({best_payer['denial_rate']:.1f}%). Providers billing this payer should "
        f"prioritize prior auth and medical necessity documentation."
    )
with i2:
    st.warning(
        f"**📋 '{top_reason}'** accounts for **{top_reason_pct:.0f}%** of all denials. "
        f"This is a process gap, not a clinical one — fixable with better intake "
        f"workflows and eligibility verification before service."
    )
with i3:
    st.info(
        f"**💸 ${gap:,.0f} gap** between total charged and total paid. "
        f"Highest-risk procedure: **{worst_proc.split(' - ')[0]}**. "
        f"Psychiatric and ER claims face the steepest denial rates."
    )

st.markdown("---")
st.caption(
    "Built by Ananya Sinha "
)