import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.title("Normal Distribution Visualiser")

# inputs
st.subheader("Input Desired Parameters")

mu = st.slider("Mean (μ) :", min_value=-10.0, max_value=10.0, value=0.0, step=0.1)
sigma = st.slider("Standard deviation (σ) :", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# Generate points

x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
y = (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu)/sigma)**2)

st.subheader("Corresponding Normal Distribution")

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Normal Distribution'))
fig.update_layout(
    title=f"Normal Distribution: μ={mu}, σ={sigma}",
    xaxis_title="x",
    yaxis_title="Probability Density"
)

st.plotly_chart(fig)