# 🛠️ Scripts Directory

This directory contains the core Python scripts that power the data generation, partitioning, upload stages of the Fraud Pipeline Patrol project.ß
---

## 📜 Script Overview

### 1. `generate_synthetic_fraud_data.py`
- **Purpose:** Generates rich, realistic synthetic data for customers, merchants, transactions, and login attempts.
- **Outputs:**
  - `data/raw/customers.parquet`
  - `data/raw/merchants.parquet`
  - `data/raw/transactions.parquet`
  - `data/raw/login_attempts.parquet`


### 2. `partition_data_with_duckdb.py`
- **Purpose:** Partitions raw Parquet files into subfolders for efficient analytics before uploading to buckets.
- **Logic:**
  - Uses DuckDB to read raw data and write partitioned Parquet files to `data/processed/`
  - Partitions by relevant columns (e.g., month, ingestion date)

### 3. `upload_fraud_data_to_minio.py`
- **Purpose:** Uploads partitioned data to MinIO (S3-compatible object storage), preserving directory structure.
- **Logic:**
  - Recursively finds all Parquet files in `data/processed/`
  - Uploads each file to the `fraud-data-processed` bucket in MinIO
  - Handles bucket creation and error logging