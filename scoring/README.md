# 🏆 Scoring Module

Welcome to the Scoring module of the Fraud Pipeline Patrol project! This component is responsible for the core fraud detection logic—analyzing enriched transaction and login data, applying risk rules, and surfacing actionable fraud alerts.

---

## ⚙️ How the Scoring Script Works

The main script, `score_transactions.py`, orchestrates the entire scoring process:

1. **Connects to Data Marts:**
   - Uses DuckDB to connect directly to Parquet marts (`v_transaction` and `v_login_attempt`) stored in MinIO/S3.

2. **Loads Data:**
   - Loads transaction and login attempt data into Pandas DataFrames for analysis.

3. **Feature Engineering:**
   - Enriches each transaction with behavioral and contextual features:
     - Recent failed login attempts
     - Geolocation mismatch
     - High-risk merchant/customer flags
     - Outlier detection on transaction amounts (z-score)
     - Odd hours, weekend, and night activity

4. **Risk Scoring:**
   - Applies a set of explainable, rule-based scoring functions to each transaction.
   - Each rule adds to the risk score and appends a flag if triggered (e.g., failed logins, geo mismatch, high-risk merchant).
   - If the total risk score exceeds a configurable threshold, the transaction is flagged as a fraud alert.

5. **Results Output:**
   - Saves all flagged alerts as a Parquet file in `data/results/fraud_alerts.parquet` for downstream analytics and dashboards.
   - Inserts alerts into the Postgres `fraud_alerts` table for further processing and notification.

---

## 🧩 Integration in the Pipeline

- The scoring script is triggered by the Airflow DAG `score_transactions_dag` after DBT marts are built and available.
- The output alerts are used by downstream modules (e.g., alerting, visualization) to notify users and monitor fraud trends.

---

## 📂 Directory Structure

```
scoring/
  README.md  ← (You are here!)
  scripts/
    score_transactions.py
  data/
    results/
      fraud_alerts.parquet
```

---

## 🎯 Why This Approach?

- **Explainability:** Rule-based scoring makes it easy to understand and audit why a transaction was flagged.
- **Configurability:** Risk rules and thresholds are easily adjustable for experimentation and tuning.
- **Performance:** DuckDB enables fast, direct querying of Parquet marts in object storage.
- **Extensibility:** New rules and features can be added with minimal code changes.

---

For more details, see the `score_transactions.py` script. Happy scoring! 🚦
