import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="My Bank Tracker", page_icon="💰", layout="centered")

# Auto-refresh on first load
if "first_load" not in st.session_state:
    st.session_state.first_load = True
    st.rerun()

st.title("💰 My Bank Tracker")

# Load saved data
DATA_FILE = "transactions.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        st.session_state.balance = data.get("balance", 1000.0)
        st.session_state.transactions = data.get("transactions", [])
else:
    st.session_state.balance = 1000.0
    st.session_state.transactions = []

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "balance": st.session_state.balance,
            "transactions": st.session_state.transactions
        }, f, indent=2)

# Callback to clear the description field safely
def clear_description():
    st.session_state.desc_input = ""

# Categories
categories = ["Food & Drink", "Rent", "Transportation", "Shopping", 
              "Entertainment", "Bills & Utilities", "Healthcare", 
              "Salary", "Other"]

st.header("Add a Transaction")
col1, col2 = st.columns(2)
with col1:
    trans_type = st.radio("Type:", ["Debit (Expense) -", "Credit (Deposit) +"])
with col2:
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")

description = st.text_input("Description", key="desc_input", placeholder="e.g. Groceries, Paycheck")
category = st.selectbox("Category", categories)

if st.button("Add Transaction", type="primary", on_click=clear_description):
    if description.strip():
        sign = -1 if "Debit" in trans_type else 1
        new_balance = st.session_state.balance + (sign * amount)
        
        if new_balance < 0 and sign == -1:
            st.error("❌ Not enough balance!")
        else:
            st.session_state.balance = new_balance
            st.session_state.transactions.append({
                "type": "Debit" if sign == -1 else "Credit",
                "description": description.strip(),
                "category": category,
                "amount": amount
            })
            save_data()
            st.success(f"✅ {trans_type} added!")
            time.sleep(0.5)
            st.rerun()
    else:
        st.error("Please enter a description!")

# Current Balance
st.header("Current Balance")
st.metric(label="💵 Remaining", value=f"${st.session_state.balance:.2f}")

# Pie Chart
st.header("Spending Breakdown")
debit_transactions = [t for t in st.session_state.transactions if t["type"] == "Debit"]

if debit_transactions:
    df_debits = pd.DataFrame(debit_transactions)
    category_totals = df_debits.groupby("category")["amount"].sum().reset_index()
    
    fig = px.pie(category_totals, 
                 values="amount", 
                 names="category", 
                 title="Debits by Category",
                 hole=0.4,
                 color_discrete_sequence=px.colors.sequential.RdBu_r)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📊 Add some debit transactions above — your spending pie chart will appear here.")

# Transaction History
st.header("Transaction History")
if st.session_state.transactions:
    for trans in reversed(st.session_state.transactions):
        emoji = "➖" if trans["type"] == "Debit" else "➕"
        st.markdown(f"**{emoji} {trans['type']}** • {trans.get('category', '—')} • {trans['description']} — **${trans['amount']:.2f}**")
else:
    st.info("No transactions yet. Add one above! 👆")

# Export to CSV
st.header("Export Data")
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    csv = df.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="📥 Download as CSV (opens in Excel/Google Sheets)",
        data=csv,
        file_name="bank_transactions.csv",
        mime="text/csv",
        type="primary"
    )
else:
    st.caption("No data to export yet.")

st.caption("Made with ❤️ in Streamlit Community Cloud")
