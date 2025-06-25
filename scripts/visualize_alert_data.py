"""
Fraud Visualization Script
--------------------------
This script connects to a Postgres database, loads fraud alert data,
and generates four visualizations:
1. Top Risky Customers
2. Most Common Fraud Flags
3. Alerts Over Time
4. Risk Score Distribution

Each chart is saved as an image in the 'visualizations/' folder.
"""

import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from pathlib import Path

# Fix: Use a safe temporary location for matplotlib cache
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"

# Step 1: Ensure output directory exists (like `mkdir -p`)
def mkdir_if_not_exists(path):
    os.makedirs(path, exist_ok=True)

# Step 2: Connect to Postgres using environment variables or defaults
def get_postgres_conn():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "airflow")
    password = os.environ.get("POSTGRES_PASSWORD", "airflow")
    db = os.environ.get("POSTGRES_DB", "airflow")

    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=db
    )

# Step 3: Load fraud alert data into a pandas DataFrame
def load_fraud_alerts():
    conn = get_postgres_conn()
    df = pd.read_sql_query("SELECT * FROM fraud_alerts;", conn)
    conn.close()
    return df

# Step 4: Preprocess data (convert timestamps, split flags into lists)
def preprocess(df):
    df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
    df['inserted_at'] = pd.to_datetime(df['inserted_at'])
    df['flags_list'] = df['flags'].str.split(',')
    return df

# Step 5: Plot Top 10 Risky Customers by Total Risk Score
def plot_top_risky_customers(df, output_path):
    top_customers = df.groupby('customer_id')['risk_score'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_customers.values, y=top_customers.index)
    plt.title("Top 10 Risky Customers (by Total Risk Score)")
    plt.xlabel("Total Risk Score")
    plt.ylabel("Customer ID")
    plt.tight_layout()
    plt.savefig(f"{output_path}/top_risky_customers.png")
    plt.close()

# Step 6: Plot Most Common Alert Flags
def plot_flag_frequencies(df, output_path):
    all_flags = df['flags_list'].explode()
    flag_counts = all_flags.value_counts()
    plt.figure(figsize=(12, 6))
    sns.barplot(x=flag_counts.values, y=flag_counts.index)
    plt.title("Most Common Fraud Alert Flags")
    plt.xlabel("Count")
    plt.ylabel("Flag")
    plt.tight_layout()
    plt.savefig(f"{output_path}/alert_flag_frequencies.png")
    plt.close()

# Step 7: Plot Weekly Alert Volume Over Time
def plot_alerts_over_time(df, output_path):
    alerts_by_week = df.set_index('transaction_timestamp').resample('W').size()
    plt.figure(figsize=(12, 6))
    plt.plot(alerts_by_week.index, alerts_by_week.values, marker='o')
    plt.title("Weekly Fraud Alerts Over Time")
    plt.xlabel("Week")
    plt.ylabel("Number of Alerts")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f"{output_path}/alerts_over_time.png")
    plt.close()

# Step 8: Plot Histogram of Risk Scores
def plot_risk_score_distribution(df, output_path):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['risk_score'], bins=10, kde=True, color='purple')
    plt.title("Distribution of Risk Scores")
    plt.xlabel("Risk Score")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{output_path}/risk_score_distribution.png")
    plt.close()

# Step 9: Run All Steps
def main():
    cwd = Path(__file__).resolve().parent.parent
    output_path = cwd / 'visualizations'
    mkdir_if_not_exists(output_path)

    print("Connecting to database and loading data...")
    df = load_fraud_alerts()

    print("Preprocessing data...")
    df = preprocess(df)

    print("Creating visualizations...")
    plot_top_risky_customers(df, output_path)
    plot_flag_frequencies(df, output_path)
    plot_alerts_over_time(df, output_path)
    plot_risk_score_distribution(df, output_path)

    print(f"All visuals saved in '{output_path}/'")

# Entry point
if __name__ == "__main__":
    main()
