"""
Fraud Detection Scoring Pipeline.

This script loads transaction and login data from MinIO, enriches the data
with features, and applies ML model scoring to identify fraudulent transactions.
The alerts are saved to both parquet files and PostgreSQL database.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

import duckdb
import joblib
import pandas as pd
import psycopg2

# Automatically load .env if present
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"), override=True
)

# sys.path.append('/opt/airflow')
# from helpers.actualdata_postgres import get_actualdata_postgres_conn

# ================================
# CONFIGURATION SECTION
# ================================
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "minioadmin")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "localhost:9000")
TRANSACTION_MART = "s3://fraud-data-processed/marts/v_transaction.parquet"
LOGIN_MART = "s3://fraud-data-processed/marts/v_login_attempt.parquet"
# Use parent directory for model path to support both /app/scoring/scripts and /opt/airflow/scoring/scripts
MODEL_PATH = str(Path(__file__).parent.parent / "fraud_model.pkl")

RISK_THRESHOLD = 5  # Used only in rule-based scoring

CONFIG = {
    "FAILED_LOGINS_WINDOW_HOURS": 24,
    "FAILED_LOGIN_THRESHOLD": 3,
    "FAILED_LOGIN_SCORE": 1,
    "GEO_MISMATCH_SCORE": 2,
    "RISKY_MERCHANT_SCORE": 2,
    "HIGH_RISK_CUSTOMER_SCORE": 2,
    "PAST_FRAUD_HISTORY_SCORE": 2,
    "ODD_HOURS_SCORE": 1,
    "AMOUNT_OUTLIER_SCORE": 2,
    "AMOUNT_ZSCORE_THRESHOLD": 3,
    "WEEKEND_LOGIN_SCORE": 1,
    "NIGHT_LOGIN_SCORE": 1,
}


# ================================
# FILE + DB HELPERS
# ================================
def ensure_dirs(dirs):
    """Create directories if they don't exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def get_actualdata_postgres_conn():
    """Connect to the actualdata-postgres service using environment variables."""
    host = os.environ.get("ACTUALDATA_POSTGRES_HOST", "actualdata-postgres")
    port = os.environ.get("ACTUALDATA_POSTGRES_PORT", "5432")
    user = os.environ.get("ACTUALDATA_POSTGRES_USER", "actualdata")
    password = os.environ.get("ACTUALDATA_POSTGRES_PASSWORD", "actualdata_pass")
    db = os.environ.get("ACTUALDATA_POSTGRES_DB", "actualdata")
    return psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname=db
    )


def create_alerts_table_if_not_exists(conn, table_name="fraud_alerts"):
    """Create fraud alerts table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
            CREATE TABLE IF NOT EXISTS {table} (
                id SERIAL PRIMARY KEY,
                transaction_id VARCHAR(255),
                customer_id VARCHAR(255),
                transaction_timestamp TIMESTAMP,
                risk_score INT,
                flags TEXT,
                inserted_at TIMESTAMP DEFAULT NOW()
            )
        """
            ).format(table=sql.Identifier(table_name))
        )
        conn.commit()


def insert_alerts_df(conn, df, table_name="fraud_alerts"):
    """Insert DataFrame of alerts into PostgreSQL table."""
    if df.empty:
        return
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                sql.SQL(
                    """
                INSERT INTO {table} (transaction_id, customer_id, transaction_timestamp, risk_score, flags, inserted_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
                ).format(table=sql.Identifier(table_name)),
                (
                    str(row["transaction_id"]),
                    str(row["customer_id"]),
                    row["transaction_timestamp"],
                    int(row["risk_score"]),
                    row["flags"],
                    datetime.now(),
                ),
            )
        conn.commit()


# ================================
# DATA LOADING & ENRICHMENT
# ================================
def connect_to_minio():
    """Connect to MinIO using DuckDB with S3 configuration."""
    con = duckdb.connect()
    # Set DuckDB home directory to /app for container compatibility
    con.execute("SET home_directory='/app';")
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    con.execute(f"SET s3_access_key_id='{S3_ACCESS_KEY}';")
    con.execute(f"SET s3_secret_access_key='{S3_SECRET_KEY}';")
    con.execute("SET s3_region='us-east-1';")
    con.execute("SET s3_url_style='path';")
    con.execute(f"SET s3_endpoint='{S3_ENDPOINT}';")
    con.execute("SET s3_use_ssl=false;")
    return con


def load_marts(con):
    """Load transaction and login data marts from MinIO."""
    tx = con.execute(
        f"SELECT * FROM '{TRANSACTION_MART}' LIMIT 5000"  # nosec B608
    ).fetchdf()
    logins = con.execute(f"SELECT * FROM '{LOGIN_MART}'").fetchdf()  # nosec B608
    tx["transaction_timestamp"] = pd.to_datetime(tx["transaction_timestamp"])
    logins["login_timestamp"] = pd.to_datetime(logins["login_timestamp"])
    return tx, logins


def enrich_transactions(transactions, logins):
    """Enrich transaction data with login patterns and risk indicators."""
    enriched = []
    for idx, tx in transactions.iterrows():
        cust_id = tx["customer_id"]
        tx_time = tx["transaction_timestamp"]

        cust_logins = logins[
            (logins["customer_id"] == cust_id) & (logins["login_timestamp"] <= tx_time)
        ]
        last_login = cust_logins.iloc[-1] if not cust_logins.empty else None

        failed_logins_24h = cust_logins[
            (
                cust_logins["login_timestamp"]
                >= tx_time - timedelta(hours=CONFIG["FAILED_LOGINS_WINDOW_HOURS"])
            )
            & (cust_logins["is_success"] is False)
        ].shape[0]

        geo_mismatch = not (
            abs(tx["latitude"] - tx["customer_home_latitude"]) < 0.01
            and abs(tx["longitude"] - tx["customer_home_longitude"]) < 0.01
        )
        odd_hours = weekend_login = night_login = False

        if last_login is not None:
            odd_hours = last_login["login_time_of_day"] == "Night (12AM-6AM)"
            weekend_login = last_login["is_weekend_login"]
            night_login = last_login.get("night_login_attempts", 0) > 0

        enriched.append(
            {
                **tx,
                "failed_logins_24h": failed_logins_24h,
                "geo_mismatch": geo_mismatch,
                "odd_hours": odd_hours,
                "weekend_login": weekend_login,
                "night_login": night_login,
            }
        )
    df_enriched = pd.DataFrame(enriched)
    print("[enrich_transactions] Sample of enriched data:")
    print(df_enriched.head())
    print("[enrich_transactions] Feature means:")
    print(
        df_enriched[
            [
                "failed_logins_24h",
                "geo_mismatch",
                "odd_hours",
                "weekend_login",
                "night_login",
            ]
        ].mean()
    )
    return df_enriched


# ================================
# SCORING FUNCTION
# ================================
def score_transactions(df):
    """Apply ML model to score transactions for fraud risk."""
    alerts = []
    print(f"Scoring {len(df)} transactions...")

    model = joblib.load(MODEL_PATH)

    # The exact order expected by the model
    feature_cols = [
        "transaction_amount",
        "failed_logins_24h",
        "geo_mismatch",
        "odd_hours",
        "weekend_login",
        "night_login",
        "is_high_risk_merchant",
        "customer_has_fraud_history",
        "customer_past_fraud_count",
    ]

    # Ensure correct types for boolean columns
    bool_cols = [
        "geo_mismatch",
        "odd_hours",
        "weekend_login",
        "night_login",
        "is_high_risk_merchant",
        "customer_has_fraud_history",
    ]
    df[bool_cols] = df[bool_cols].astype(int)

    X = df[feature_cols].copy()
    y_pred = model.predict(X)
    print(f"Model predictions: {y_pred}")

    for idx, tx in df.iterrows():
        if y_pred[idx] == 1.0:
            alerts.append(
                {
                    "transaction_id": tx.get("transaction_id", idx),
                    "customer_id": tx.get("customer_id", None),
                    "transaction_timestamp": tx.get("transaction_timestamp", None),
                    "risk_score": 1,
                    "flags": "ML_MODEL",
                }
            )

    return pd.DataFrame(alerts)


# ================================
# MAIN PIPELINE EXECUTION
# ================================
if __name__ == "__main__":
    print("Starting scoring pipeline...")

    con = connect_to_minio()
    transactions, logins = load_marts(con)
    print(f"Loaded {len(transactions)} transactions and {len(logins)} login attempts.")

    enriched = enrich_transactions(transactions, logins)
    alerts = score_transactions(enriched)

    print(f"\nScoring complete. Number of alerts: {len(alerts)}")
    print(alerts.head())

    cwd = Path(__file__).resolve().parent.parent.parent
    results_dir = cwd / "data" / "results"
    ensure_dirs([results_dir])
    alerts.to_parquet(results_dir / "fraud_alerts.parquet", index=False)
    print("Alerts saved to data/results/fraud_alerts.parquet.")

    try:
        pg_conn = get_actualdata_postgres_conn()
        create_alerts_table_if_not_exists(pg_conn)
        insert_alerts_df(pg_conn, alerts)
        pg_conn.close()
        print("Alerts saved to Postgres table 'fraud_alerts'.")
    except Exception as e:
        print(f"Failed to save alerts to Postgres: {e}")
