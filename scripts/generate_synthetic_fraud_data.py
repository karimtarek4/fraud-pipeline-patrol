"""
generate_synthetic_fraud_data.py.

This script creates a rich synthetic dataset for a rule-based fraud detection pipeline.
It outputs four files in data/raw/:
  - customers.parquet       : Customer profiles with SCD2 fields & batch metadata
  - merchants.parquet       : Merchant info with risk scores & batch metadata
  - transactions.parquet    : Transaction records with engineered features & batch metadata
  - login_attempts.parquet  : Individual failed-login events for separate modeling
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd


def ensure_dirs(dirs):
    """Create each directory in `dirs` if it doesn't already exist."""
    """Create each directory in `dirs` if it doesn't already exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def return_current_ingestion_date():
    """Generate batch metadata: current timestamp."""
    return pd.Timestamp.now()


def generate_customers(start_id=1001, num_customers=1000):
    """Build a customer profile table with behavioral baselines and metadata."""
    # Base demographics
    df = pd.DataFrame(
        {
            # arrange: evenly spaced
            "CustomerID": np.arange(start_id, start_id + num_customers),
            "AccountCreationDate": pd.date_range(
                "2020-01-01", periods=num_customers, freq="D"
            ),
            "Age": np.random.randint(18, 65, num_customers),
        }
    )

    # Add AccountCreationMonth field
    df["AccountCreationMonth"] = df["AccountCreationDate"].dt.month

    # Behavioral baselines
    # choice: conitnous
    df["AvgTransactionAmount"] = np.random.uniform(50, 200, num_customers)
    # choice: probability
    df["PastFraudCount"] = np.random.choice(
        [0, 1, 2], num_customers, p=[0.9, 0.08, 0.02]
    )
    # for _ in: number of times
    df["HomeDevice"] = [
        f"dev_{np.random.randint(1000,9999)}" for _ in range(num_customers)
    ]
    df["HomeIP"] = [
        f"192.168.{np.random.randint(0,255)}.{np.random.randint(0,255)}"
        for _ in range(num_customers)
    ]
    df["HomeLat"] = np.random.uniform(30.0, 45.0, num_customers)
    df["HomeLon"] = np.random.uniform(-100.0, -70.0, num_customers)

    # SCD2 effective dating & batch metadata
    ingestion_date = return_current_ingestion_date()
    df["ingestion_date"] = ingestion_date

    return df


def generate_merchants(start_id=2001, num_merchants=1000):
    """Build a merchant table with category and risk score information."""
    ids = np.arange(start_id, start_id + num_merchants)
    categories = ["Groceries", "Retail", "Travel", "Online", "Gambling", "Crypto"]
    risk_map = {
        "Groceries": 0.1,
        "Retail": 0.2,
        "Travel": 0.15,
        "Online": 0.25,
        "Gambling": 0.8,
        "Crypto": 0.7,
    }

    df = pd.DataFrame(
        {
            "MerchantID": ids,
            "MerchantName": [f"Merchant_{mid}" for mid in ids],
            "Category": np.random.choice(categories, num_merchants),
        }
    )
    df["MerchantRiskScore"] = df["Category"].map(risk_map)

    ingestion_date = return_current_ingestion_date()
    df["ingestion_date"] = ingestion_date

    return df


def random_timestamps(start, count, scale_seconds=3600):
    """Generate timestamps using exponential inter-arrival times."""
    intervals = np.random.exponential(scale=scale_seconds, size=count)
    elapsed = np.cumsum(intervals)
    return start + pd.to_timedelta(elapsed, unit="s")


def generate_transactions(customers, merchants, avg_txs_per_cust=5.0):
    """Build a transactions table with rich features and fraud indicators."""
    records = []
    tx_id = 1
    ingestion_date = return_current_ingestion_date()

    # Create yearly timestamp range
    year_start = pd.Timestamp("2022-01-01")
    year_end = pd.Timestamp("2022-12-31")
    year_range_seconds = (year_end - year_start).total_seconds()

    for _, cust in customers.iterrows():
        # poisson: You might get 3, 7, 1, or even 0 by chance so it averages 5.
        # max: ensures you never drop to zero.
        count = max(1, np.random.poisson(lam=avg_txs_per_cust))

        # Generate random start points throughout the year
        random_starts = []
        for _ in range(count):
            # Pick a random point in the year
            random_seconds = np.random.uniform(0, year_range_seconds)
            random_start = year_start + pd.Timedelta(seconds=random_seconds)
            random_starts.append(random_start)

        # Sort the timestamps to maintain chronological order per customer
        random_starts.sort()

        # build customer transactions, using random timestamps throughout the year
        for ts in random_starts:
            # loc: mean position
            # scale: standard deviation from mean
            amt = np.random.normal(
                loc=cust["AvgTransactionAmount"],
                scale=0.3 * cust["AvgTransactionAmount"],
            )
            amt = abs(amt) if amt > 1 else 1.0

            # Device & IP hops
            device = (
                cust["HomeDevice"]
                if np.random.rand() < 0.9
                else f"dev_{np.random.randint(1000,9999)}"
            )
            ip = (
                cust["HomeIP"]
                if np.random.rand() < 0.9
                else f"10.0.{np.random.randint(0,255)}.{np.random.randint(0,255)}"
            )

            # Geolocation jitter vs drift
            if np.random.rand() < 0.9:
                # Jitter: small noise around home
                lat = cust["HomeLat"] + np.random.normal(0, 0.01)
                lon = cust["HomeLon"] + np.random.normal(0, 0.01)
            else:
                # Drift: large jump away from home
                lat = cust["HomeLat"] + np.random.uniform(1, 5)
                lon = cust["HomeLon"] + np.random.uniform(1, 5)

            channel = np.random.choice(["Online", "POS", "ATM", "MobileApp", "Web"])
            # if 95% chance: lam 0.5 -> [0, 1] else avg = 5
            fails = np.random.poisson(lam=0.5 if np.random.rand() > 0.05 else 5)

            # sample: random
            # iloc[0]: return series
            merch = merchants.sample(1).iloc[0]

            records.append(
                {
                    "TransactionID": tx_id,
                    "CustomerID": cust["CustomerID"],
                    "Timestamp": ts,
                    "TimestampMonth": ts.month,
                    "TransactionAmount": float(amt),
                    "DeviceID": device,
                    "IP_Address": ip,
                    "Lat": lat,
                    "Lon": lon,
                    "Channel": channel,
                    "MerchantID": int(merch["MerchantID"]),
                    "FailedTransactions": int(fails),
                    "ingestion_date": ingestion_date,
                }
            )
            tx_id += 1

    return pd.DataFrame(records)


def generate_login_attempts(transactions):
    """Generate individual failed login attempt records from transaction data."""
    logs = []
    ingestion_date = transactions["ingestion_date"].iat[0]

    for _, tx in transactions.iterrows():
        for _ in range(tx["FailedTransactions"]):
            delta = np.random.exponential(scale=60)
            lt = tx["Timestamp"] - pd.Timedelta(seconds=delta)
            logs.append(
                {
                    "CustomerID": tx["CustomerID"],
                    "LoginTimestamp": lt,
                    "LoginTimestampMonth": lt.month,
                    "Success": False,
                    "ingestion_date": ingestion_date,
                }
            )

    return pd.DataFrame(logs)


def main():
    """Generate synthetic fraud detection dataset and save to parquet files."""
    cwd = Path(__file__).resolve().parent.parent
    raw_dir = cwd / "data" / "raw"
    print(f"Writing data to {raw_dir}")
    ensure_dirs([raw_dir])

    customers = generate_customers()
    merchants = generate_merchants()
    transactions = generate_transactions(customers, merchants)
    login_attempts = generate_login_attempts(transactions)

    # Remove FailedTransactions from transactions table now that login_attempts exist
    transactions = transactions.drop(columns=["FailedTransactions"])

    # Write out all tables to Parquet
    customers.to_parquet(f"{raw_dir}/customers.parquet", index=False)
    merchants.to_parquet(f"{raw_dir}/merchants.parquet", index=False)
    transactions.to_parquet(f"{raw_dir}/transactions.parquet", index=False)
    login_attempts.to_parquet(f"{raw_dir}/login_attempts.parquet", index=False)

    print(
        f"Wrote {len(customers)} customers, "
        f"{len(merchants)} merchants, "
        f"{len(transactions)} transactions, "
        f"{len(login_attempts)} login attempts."
    )


if __name__ == "__main__":
    main()
