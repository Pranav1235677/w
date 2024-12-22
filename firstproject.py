import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Function to generate a realistic dataset for a given month
def generate_data_for_month(month, n=200):
    categories = [
        "Food", "Transportation", "Bills", "Groceries", "Entertainment",
        "Healthcare", "Shopping", "Travel", "Dining", "Subscriptions"
    ]
    payment_modes = [
        "Cash", "Wallet", "Credit Card", "Debit Card", "UPI", "Netbanking"
    ]
    data = []
    for _ in range(n):
        data.append({
            "Date": fake.date_this_year(),
            "Category": random.choice(categories),
            "Payment_Mode": random.choice(payment_modes),
            "Description": fake.text(max_nb_chars=30),
            "Amount_Paid": round(random.uniform(50.0, 1000.0), 2),
            "Cashback": round(random.uniform(0.0, 50.0), 2),
            "Month": month
        })
    return pd.DataFrame(data)

# Function to initialize the SQLite database
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            Date TEXT,
            Category TEXT,
            Payment_Mode TEXT,
            Description TEXT,
            Amount_Paid REAL,
            Cashback REAL,
            Month TEXT
        )
    """)
    conn.commit()
    conn.close()

# Function to load data into the database
def load_data_for_all_months():
    conn = sqlite3.connect('expenses.db')
    for month in [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]:
        data = generate_data_for_month(month, n=200)
        data.to_sql('expenses', conn, if_exists='append', index=False)
    conn.close()
    st.success("Data for all months has been generated and loaded into the database!")

# Function to query data from the database
def query_data(query):
    conn = sqlite3.connect('expenses.db')
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# Predefined SQL Queries
SQL_QUERIES = {
    "Total Amount Spent per Category": "SELECT Category, SUM(Amount_Paid) AS Total_Spent FROM expenses WHERE Month = '{}' GROUP BY Category",
    "Payment Mode Distribution": "SELECT Payment_Mode, COUNT(*) AS Transaction_Count, SUM(Amount_Paid) AS Total_Spent FROM expenses WHERE Month = '{}' GROUP BY Payment_Mode",
    "Spending Trends Over Time": "SELECT Date, SUM(Amount_Paid) AS Daily_Spent FROM expenses WHERE Month = '{}' GROUP BY Date ORDER BY Date",
}

# Main Streamlit app
st.title("Advanced Expense Tracker")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose an option",
    [
        "Load Data for All Months", "View Data", "Predefined SQL Queries"
    ]
)

if option == "Load Data for All Months":
    st.subheader("Load Data for All Months")
    if st.button("Load Data"):
        init_db()
        load_data_for_all_months()

elif option == "View Data":
    st.subheader("View Expense Data")
    month = st.selectbox("Select a month to view data:", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    query = f"SELECT * FROM expenses WHERE Month = '{month}'"
    data = query_data(query)
    st.dataframe(data)

elif option == "Predefined SQL Queries":
    st.subheader("Predefined SQL Queries")
    month = st.selectbox("Select the month:", [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    query_name = st.selectbox("Select a query to run", list(SQL_QUERIES.keys()))
    query = SQL_QUERIES[query_name].format(month)
    if st.button("Run Query"):
        data = query_data(query)
        st.dataframe(data)
        if query_name == "Spending Trends Over Time":
            st.line_chart(data.set_index("Date"))
        elif query_name in ["Total Amount Spent per Category", "Payment Mode Distribution"]:
            st.bar_chart(data.set_index(data.columns[0]))