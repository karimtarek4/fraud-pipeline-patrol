# 📁 `data/` Directory

The `data/` directory is the **source of truth** for all raw and processed data used in early stages of fraud detection pipeline. It contains:

---

## 1. `generate_synthetic_fraud_data.py`

A Python script that **generates a rich synthetic dataset** for the project. When executed, it:

* Creates **customer profiles** with SCD2 fields and behavioral baselines.
* Builds a **merchant table** with risk scores per category.
* Produces **transaction records** that include:
* Writes out **Parquet** files (with CSV fallback) under 

## 2. `data/raw/`:

  * `customers.parquet` 
  * `merchants.parquet` 
  * `transactions.parquet` 
  * `login_attempts.parquet` 

---

## 3. `data/processed/` 

Contains **partitioned data** from `data/raw/` that has been processed and partitioned by **DuckDB** via the `partition_data_with_duckdb.py` script. This directory maintains the same data structure but with improved organization:

* `customers/` - Partitioned customer data from `customers.parquet`
* `merchants/` - Partitioned merchant data from `merchants.parquet` 
* `transactions/` - Partitioned transaction data from `transactions.parquet`
* `login_attempts/` - Partitioned login attempt data from `login_attempts.parquet`

The partitioning improves query performance and data organization.

---

This folder holds the data before upload to bucket.