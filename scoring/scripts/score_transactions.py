
import duckdb
import pandas as pd
from datetime import timedelta
from pathlib import Path
import os
from psycopg2 import sql
from datetime import datetime
import sys
sys.path.append('/opt/airflow')
from helpers.actualdata_postgres import get_actualdata_postgres_conn

# ================================
# CONFIGURATION SECTION
# ================================
# These are your MinIO/S3 and data mart connection settings.
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "localhost:9000")
TRANSACTION_MART = "s3://fraud-data-processed/marts/v_transaction.parquet"
LOGIN_MART = "s3://fraud-data-processed/marts/v_login_attempt.parquet"
RISK_THRESHOLD = 5  # Any transaction with this score or higher will be flagged as risky

# You can change these parameters to adjust the risk rules.
CONFIG = {
    "FAILED_LOGINS_WINDOW_HOURS": 24,  # How far back to look for failed logins
    "FAILED_LOGIN_THRESHOLD": 3,       # Number of failed logins to consider risky
    "FAILED_LOGIN_SCORE": 1,           # Score if failed login threshold is crossed
    "GEO_MISMATCH_SCORE": 2,           # Score if locations don't match
    # "DEVICE_MISMATCH_SCORE": 1,        # Score if devices don't match
    # "CHANNEL_CHANGE_SCORE": 1,         # Score if channel seems unusual
    "RISKY_MERCHANT_SCORE": 2,         # Score for high risk merchant
    "HIGH_RISK_CUSTOMER_SCORE": 2,     # Score for high/medium risk customer
    "PAST_FRAUD_HISTORY_SCORE": 2,     # Score for past fraud by customer
    "ODD_HOURS_SCORE": 1,              # Score for activity at odd hours
    "AMOUNT_OUTLIER_SCORE": 2,         # Score for unusually large/small amounts
    "AMOUNT_ZSCORE_THRESHOLD": 3,      # How "unusual" an amount has to be (statistical outlier)
    "WEEKEND_LOGIN_SCORE": 1,          # Score for weekend login
    "NIGHT_LOGIN_SCORE": 1,            # Score for night-time login
}

def ensure_dirs(dirs):
    """Create each directory in `dirs` if it doesn't already exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def create_alerts_table_if_not_exists(conn, table_name="fraud_alerts"):
    """
    Create the alerts table if it doesn't exist.
    """
    with conn.cursor() as cur:
        cur.execute(sql.SQL(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(255),
                customer_id VARCHAR(255),
                transaction_timestamp TIMESTAMP,
                risk_score INT,
                flags TEXT,
                inserted_at TIMESTAMP DEFAULT NOW()
            )
        '''))
        conn.commit()

def insert_alerts_df(conn, df, table_name="fraud_alerts"):
    """
    Insert the alerts DataFrame into the Postgres table.
    """
    if df.empty:
        return
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(sql.SQL(f'''
                INSERT INTO {table_name} (transaction_id, customer_id, transaction_timestamp, risk_score, flags, inserted_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''), (
                str(row['transaction_id']),
                str(row['customer_id']),
                row['transaction_timestamp'],
                int(row['risk_score']),
                row['flags'],
                datetime.now()
            ))
        conn.commit()

# ================================
# CONNECT TO MINIO VIA DUCKDB
# ================================
def connect_to_minio():
    """
    Connect to MinIO (S3-compatible) storage using DuckDB.
    This allows DuckDB to read your Parquet files directly from object storage.
    """
    con = duckdb.connect()
    con.execute(f"SET s3_access_key_id='{S3_ACCESS_KEY}';")
    con.execute(f"SET s3_secret_access_key='{S3_SECRET_KEY}';")
    con.execute("SET s3_region='us-east-1';")
    con.execute("SET s3_url_style='path';")
    con.execute(f"SET s3_endpoint='{S3_ENDPOINT}';")
    con.execute("SET s3_use_ssl=false;")
    return con

# ================================
# LOAD DATA FROM PARQUET MARTS
# ================================
def load_marts(con):
    """
    Load transaction and login mart data as Pandas DataFrames.
    Convert their timestamp columns to datetime type for easier comparisons.
    """
    tx = con.execute(f"SELECT * FROM '{TRANSACTION_MART}' Limit 1000").fetchdf()
    logins = con.execute(f"SELECT * FROM '{LOGIN_MART}'").fetchdf()
    tx['transaction_timestamp'] = pd.to_datetime(tx['transaction_timestamp'])
    logins['login_timestamp'] = pd.to_datetime(logins['login_timestamp'])
    return tx, logins

# ================================
# FEATURE ENGINEERING
# ================================
def enrich_transactions(transactions, logins):
    """
    For each transaction, create new features using both transaction and login data.
    - Looks up the latest login for each customer.
    - Calculates failed logins, device mismatch, location mismatch, channel change, and time-of-day risk.
    Returns a new DataFrame with all these extra features.
    """
    enriched = []
    for idx, tx in transactions.iterrows():
        cust_id = tx['customer_id']
        tx_time = tx['transaction_timestamp']
        tx_device = tx['device_id']
        tx_channel = tx['channel']
        tx_lat = tx['latitude']
        tx_long = tx['longitude']

        # Select logins for this customer that happened before this transaction
        cust_logins = logins[(logins['customer_id'] == cust_id) & 
                             (logins['login_timestamp'] <= tx_time)]
        last_login = cust_logins.iloc[-1] if not cust_logins.empty else None

        # Count failed logins in the last N hours
        # Look for failed logins between tx and tx - 24 hrs
        # Shape returns count 
        failed_logins_24h = cust_logins[
            (cust_logins['login_timestamp'] >= tx_time - timedelta(hours=CONFIG["FAILED_LOGINS_WINDOW_HOURS"])) &
            (cust_logins['is_success'] == False)
        ].shape[0]

        # Feature defaults
        geo_mismatch = False
        # device_mismatch = False
        # channel_change = False
        odd_hours = False
        weekend_login = False
        night_login = False

        # Only calculate these features if we have a login
        if last_login is not None:
            # Geo mismatch: transaction location different from customer home location
            geo_mismatch = not (
                abs(tx['latitude'] - tx['customer_home_latitude']) < 0.01 and
                abs(tx['longitude'] - tx['customer_home_longitude']) < 0.01
            )
            # Device mismatch: device used for transaction is not the same as in the last login
            # (if you have device_id in login mart, change to last_login['device_id'])
            # device_mismatch = tx_device != last_login['customer_id']  # <-- update as needed
            # Channel change: if transaction channel is not typical for that customer/time
            # (this is a placeholder check)
            # channel_change = tx_channel.lower() not in (last_login.get('login_time_of_day', '').lower() if 'login_time_of_day' in last_login else '')
            # Odd hours: last login happened at night
            odd_hours = last_login['login_time_of_day'] == 'Night (12AM-6AM)'
            weekend_login = last_login['is_weekend_login']
            night_login = last_login.get('night_login_attempts', 0) > 0

        # Add all features to the transaction
        enriched.append({
            **tx,
            'failed_logins_24h': failed_logins_24h,
            'geo_mismatch': geo_mismatch,
            # 'device_mismatch': device_mismatch,
            # 'channel_change': channel_change,
            'odd_hours': odd_hours,
            'weekend_login': weekend_login,
            'night_login': night_login,
            # Carry over high-risk merchant/customer features
            'is_high_risk_merchant': tx['is_high_risk_merchant'],
            'merchant_risk': tx['merchant_risk_category'],
            'customer_risk_level': tx['customer_risk_level'],
            'customer_has_fraud_history': tx['customer_has_fraud_history'],
            'customer_past_fraud_count': tx['customer_past_fraud_count'],
        })
    return pd.DataFrame(enriched)

# ================================
# CALCULATE AMOUNT Z-SCORES
# ================================
def compute_z_scores(df):
    """
    For each customer, calculate how unusual the transaction amount is compared to their average.
    This uses the z-score formula. The higher the z-score, the more unusual the transaction.
    """
    df['amount_zscore'] = df.groupby('customer_id')['transaction_amount'].transform(
        lambda x: (x - x.mean()) / (x.std(ddof=0) if x.std(ddof=0) else 1)
    )
    return df

# ================================
# FRAUD RISK SCORING
# ================================
def score_transactions(df):
    """
    Apply simple, explainable rules to assign a risk score to each transaction.
    If the score passes the threshold, the transaction is flagged as an alert.
    Returns a DataFrame of flagged transactions with their scores and triggered rules.
    """
    alerts = []
    for idx, tx in df.iterrows():
        score = 0
        flags = []

        # Rule 1: Many failed logins recently
        if tx['failed_logins_24h'] > CONFIG["FAILED_LOGIN_THRESHOLD"]:
            score += CONFIG["FAILED_LOGIN_SCORE"]
            flags.append("FAILED_LOGIN")

        # Rule 2: Location doesn't match customer profile
        if tx['geo_mismatch']:
            score += CONFIG["GEO_MISMATCH_SCORE"]
            flags.append("GEO_MISMATCH")

        # Rule 3: Device used isn't the same
        # if tx['device_mismatch']:
        #     score += CONFIG["DEVICE_MISMATCH_SCORE"]
        #     flags.append("DEVICE_MISMATCH")

        # Rule 4: Unusual channel used
        # if tx['channel_change']:
        #     score += CONFIG["CHANNEL_CHANGE_SCORE"]
        #     flags.append("CHANNEL_CHANGE")

        # Rule 5: High-risk merchant
        if tx['is_high_risk_merchant']:
            score += CONFIG["RISKY_MERCHANT_SCORE"]
            flags.append("HIGH_RISK_MERCHANT")

        # Rule 6: High-risk customer
        if tx['customer_risk_level'] in ("High", "Medium"):
            score += CONFIG["HIGH_RISK_CUSTOMER_SCORE"]
            flags.append("CUSTOMER_RISK")

        # Rule 7: Customer has past fraud history
        if tx['customer_has_fraud_history'] or tx['customer_past_fraud_count'] > 0:
            score += CONFIG["PAST_FRAUD_HISTORY_SCORE"]
            flags.append("PAST_FRAUD")

        # Rule 8: Activity at odd hours
        if tx['odd_hours']:
            score += CONFIG["ODD_HOURS_SCORE"]
            flags.append("ODD_HOURS")

        # Rule 9: Weekend login
        if tx['weekend_login']:
            score += CONFIG["WEEKEND_LOGIN_SCORE"]
            flags.append("WEEKEND_LOGIN")

        # Rule 10: Night login
        if tx['night_login']:
            score += CONFIG["NIGHT_LOGIN_SCORE"]
            flags.append("NIGHT_LOGIN")

        # Rule 11: Transaction amount is a big outlier
        if abs(tx['amount_zscore']) > CONFIG["AMOUNT_ZSCORE_THRESHOLD"]:
            score += CONFIG["AMOUNT_OUTLIER_SCORE"]
            flags.append("AMOUNT_OUTLIER")

        # If the score is high enough, add to alerts
        if score >= RISK_THRESHOLD:
            alerts.append({
                'transaction_id': tx['transaction_id'],
                'customer_id': tx['customer_id'],
                'transaction_timestamp': tx['transaction_timestamp'],
                'risk_score': score,
                'flags': ",".join(flags),
            })
    return pd.DataFrame(alerts)

# ================================
# MAIN PIPELINE EXECUTION
# ================================
if __name__ == "__main__":
    print("Starting scoring pipeline...")

    # Step 1: Connect to storage
    con = connect_to_minio()
    # Step 2: Load data from marts
    transactions, logins = load_marts(con)
    print(f"Loaded {len(transactions)} transactions and {len(logins)} login attempts.")

    # Step 3: Enrich transactions with login and profile features
    enriched = enrich_transactions(transactions, logins)
    # Step 4: Calculate outlier scores for transaction amounts
    enriched = compute_z_scores(enriched)
    # Step 5: Score each transaction and flag the risky ones
    alerts = score_transactions(enriched)

    print(f"\nScoring complete. Number of alerts: {len(alerts)}")
    print(alerts.head())

    # Step 6: Save alerts for downstream use (BI, dashboard, notifications, etc.)
    cwd = Path(__file__).resolve().parent.parent.parent
    results_dir = cwd / 'data' / 'results'
    ensure_dirs([results_dir])
    alerts.to_parquet(results_dir / 'fraud_alerts.parquet', index=False)
    print("Alerts saved to data/results/fraud_alerts.parquet.")

    # Step 7: Save alerts to Postgres
    try:
        pg_conn = get_actualdata_postgres_conn()
        create_alerts_table_if_not_exists(pg_conn)
        insert_alerts_df(pg_conn, alerts)
        pg_conn.close()
        print("Alerts saved to Postgres table 'fraud_alerts'.")
    except Exception as e:
        print(f"Failed to save alerts to Postgres: {e}")
