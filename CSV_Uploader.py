import streamlit as st
import pandas as pd
import numpy as np

st.title("CSV Uploader")

data = st.file_uploader("Upload a CSV", type="csv")

if data is not None:
    df = pd.read_csv(data)
    st.dataframe(df)
    
    st.subheader("Summary Statistics")
    st.write(df.describe())
else:
    st.write("Please upload a CSV file to get started")





