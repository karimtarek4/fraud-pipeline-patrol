# 🛠️ Scripts Directory

This directory contains the core Python scripts that power the data generation, partitioning, upload, and visualization stages of the Fraud Pipeline Patrol project. Each script is modular, well-documented, and designed for seamless integration with the overall pipeline.

---

## 📜 Script Overview

### 1. `generate_synthetic_fraud_data.py`
- **Purpose:** Generates rich, realistic synthetic data for customers, merchants, transactions, and login attempts.
- **Outputs:**
  - `data/raw/customers.parquet`
  - `data/raw/merchants.parquet`
  - `data/raw/transactions.parquet`
  - `data/raw/login_attempts.parquet`
- **Highlights:**
  - Simulates behavioral baselines, geolocation, device/IP, and risk factors
  - Supports SCD2 fields and batch metadata for incremental pipelines
  - Ensures reproducibility and extensibility

### 2. `partition_data_with_duckdb.py`
- **Purpose:** Partitions raw Parquet files into subfolders for efficient analytics and downstream processing.
- **Logic:**
  - Uses DuckDB to read raw data and write partitioned Parquet files to `data/processed/`
  - Partitions by relevant columns (e.g., month, ingestion date)

### 3. `upload_fraud_data_to_minio.py`
- **Purpose:** Uploads partitioned data to MinIO (S3-compatible object storage), preserving directory structure.
- **Logic:**
  - Recursively finds all Parquet files in `data/processed/`
  - Uploads each file to the `fraud-data-processed` bucket in MinIO
  - Handles bucket creation and error logging

### 4. `visualize_alert_data.py`
- **Purpose:** Generates actionable fraud visualizations from the `fraud_alerts` table in Postgres.
- **Visuals Produced:**
  - Top 10 risky customers
  - Most common fraud alert flags
  - Alerts over time
  - Risk score distribution
- **Output:**
  - All charts are saved as PNG images in the `visualizations/` directory

---

## 🔗 Integration
- These scripts are orchestrated by Airflow DAGs and are key building blocks of the pipeline.
- Each script can be run independently for development and testing.

---

## 🚀 How to Use
- Ensure all dependencies are installed (see project requirements).
- Run each script from the project root or as part of the Airflow pipeline.
- Outputs will be saved in the appropriate data or visualizations directories.

---

## 📝 Notes
- Scripts are designed for clarity, modularity, and extensibility.
- For more details, see the docstrings and comments within each script.

---
