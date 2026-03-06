import streamlit as st
import json
import os
import time

st.set_page_config(page_title="My Bank Tracker", page_icon="💰", layout="centered")

# Auto-refresh on first load
if "first_load" not in st.session_state:
    st.session_state.first_load = True
    st.rerun()

st.title("💰 My Bank Tracker")
st.markdown("**Credits & Debits** • Data saved permanently")

# Load data from JSON file (persists forever)
DATA_FILE = "transactions.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        if 'balance' not in st.session_state:
            st.session_state.balance = data.get("balance", 1000.0)
        if 'transactions' not in st.session_state:
            st.session_state.transactions = data.get("transactions", [])
else:
    if 'balance' not in st.session_state:
        st.session_state.balance = 1000.0
    if 'transactions' not in st.session_state:
        st.session_state.transactions = []

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "balance": st.session_state.balance,
            "transactions": st.session_state.transactions
        }, f, indent=2)

st.header("Add a Transaction")
col1, col2 = st.columns(2)
with col1:
    trans_type = st.radio("Type:", ["Debit (Expense) -", "Credit (Deposit) +"])
with col2:
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")

description = st.text_input("Description (e.g. Paycheck, Coffee, Rent)")

if st.button("Add Transaction", type="primary"):
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
                "amount": amount
            })
            save_data()  # ← This saves permanently!
            st.success(f"✅ {trans_type} added!")
            time.sleep(0.6)
            st.rerun()
    else:
        st.error("Please enter a description!")

st.header("Current Balance")
st.metric(label="💵 Remaining", value=f"${st.session_state.balance:.2f}")

st.header("Transaction History")
if st.session_state.transactions:
    for trans in reversed(st.session_state.transactions):
        emoji = "➖" if trans["type"] == "Debit" else "➕"
        st.markdown(f"**{emoji} {trans['type']}**: {trans['description']} — **${trans['amount']:.2f}**")
else:
    st.info("No transactions yet. Add one above! 👆")

st.caption("Made with ❤️ in Streamlit Community Cloud • Data saved forever on GitHub")
