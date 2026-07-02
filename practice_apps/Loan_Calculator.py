import streamlit as st
import numpy as np
import pandas as pd

# Assumptions:
# Nominal interest rate compounded monthly i.e. i^(12)
# Loan term is yearly, must convert to months
# Immediate annuity

st.title("Loan Calculator")

st.subheader("Inputs")
loan_amount = st.number_input("Loan amount (£):", min_value=1000, value=10000, step=1000) # sets a min, value automatically shows when opens, step for when pressing up/down arrows
interest_rate = st.number_input("Annual interest rate (%):", min_value=0.1, value=5.0, step=0.1)
loan_term = st.number_input("Loan term (years):", min_value=1, value=25, step=1)

# Calculations
n = loan_term * 12 # Yearly -> Monthly
i_p = interest_rate/100 # 5% -> 0.05
i = i_p / 12 # Monthly rate 
Discount_factor = 1/(1+i) # Get v
annuity = (1-Discount_factor**n)/i #a_n
premium = loan_amount / annuity # C/a_n

def amount_outstanding(m):
   amount_outstanding = loan_amount-(premium * ((1-Discount_factor**m)/i))
   return amount_outstanding

def interest_paid(m):
    interest_paid = amount_outstanding(m-1)*(i)
    return interest_paid

st.subheader("Results")
st.metric("Monthly payment", f"£{premium:,.2f}")

# Build full loan schedule 
months = list(range(1, int(n)+1))
outstanding = [amount_outstanding(m) for m in months]
interest = [interest_paid(m) for m in months]
principal = [premium - interest_paid(m) for m in months]

total_interest = sum(interest)
total_repaid = loan_amount + total_interest

st.metric("Total repaid", f"£{total_repaid:,.2f}")
st.metric("Total interest paid", f"£{total_interest}")

st.title("Full Schedule of Payments")
schedule = pd.DataFrame({
   "Month": months,
   "Amount Outstanding (£)": [f"{x:,.2f}" for x in outstanding],
   "Interest Paid (£)": [f"{x:,.2f}" for x in interest],
   "Principal Repaid (£)": [f"{x:,.2f}" for x in principal]
})

st.dataframe(schedule) 









