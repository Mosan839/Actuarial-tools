import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

try:
    import plotly.graph_objects as go
    import numpy as np
    from funding_level import run_simulation
except Exception as e:
    st.error(f"Startup error: {e}")
    st.stop()

st.title("Conecast - scheme funding stochastic projector")

# Inputs

starting_asset = st.sidebar.number_input("Starting assets (£)", value=80_000_000, step=1_000_000, format="%d")
starting_liabiities = st.sidebar.number_input("Starting liabilies (£):", value = 100_000_000, step=1_000_000, format="%d")
equity_allocation = st.sidebar.slider("Equity allocation %", min_value= 0, max_value= 100, value= 50)
bond_allocation = st.sidebar.slider("Bond allocation %", min_value= 0, max_value= 100, value= 40)
cash = 100 - equity_allocation - bond_allocation
if cash < 0:
    st.sidebar.warning("Equity + bond allocation exceeds 100%. Reduce one of them.")
    st.stop()
else: st.sidebar.write("Cash %:", cash)
liability_duration = st.sidebar.slider("Liability duration (in years)",min_value= 5, max_value= 30, value= 15)
n_sim = st.sidebar.slider("Number of simulations",min_value= 100, max_value= 5000, value = 1000)
n_years = st.sidebar.slider("Number of years simulated",min_value= 5, max_value= 30, value= 20)


# Run simulation

results = run_simulation(
    starting_assets= starting_asset,
    starting_liabilities=starting_liabiities,
    asset_allocation={"equity": equity_allocation /100, "bond": bond_allocation /100, "cash": cash /100},
    liability_duration= liability_duration,
    n_years= n_years,
    n_sims= n_sim,
    seed=42,
)

# Building plotly chart (cone) 

starting_fl = (starting_asset / starting_liabiities) * 100
st.metric("Starting funding level", f"{starting_fl:.1f}%")

df = results["percentile_table"]
fig = go.Figure()

# P90 line (top of cone)
fig.add_trace(go.Scatter(x=df["year"], y=df["p90"], name="90th percentile", line=dict(color="green", dash="dash")))

# P10 line (bottom of cone) — add this yourself, same pattern as above
fig.add_trace(go.Scatter(x=df["year"], y=df["p10"], name="10th percentile", line=dict(color="green", dash="dash")))

# P50 line (median) — add this yourself, make it a solid line, different colour
fig.add_trace(go.Scatter(x=df["year"], y=df["p50"], name="50th percentile", line=dict(color="blue")))
# Cone fill between P10 and P90
fig.add_trace(go.Scatter(
    x=list(df["year"]) + list(df["year"][::-1]),
    y=list(df["p90"]) + list(df["p10"][::-1]),
    fill="toself",
    fillcolor="rgba(0,200,100,0.1)",
    line=dict(color="rgba(255,255,255,0)"),
    name="P10–P90 range",
))

# Full funding reference line at y=1.0
fig.add_hline(y=1.0, line_dash="dot", line_color="red", annotation_text="Full funding (100%)")

fig.update_layout(
    title="Projected Funding Level — Cone of Uncertainty",
    xaxis_title="Year",
    yaxis_title="Funding Level",
    yaxis_tickformat=".0%",
)

st.plotly_chart(fig, use_container_width=True)

# Percentile table

st.subheader("Percentile table")
st.dataframe(results["percentile_table"].style.format({
    "p10": "{:.1%}", "p50": "{:.1%}", "p90": "{:.1%}"
}))