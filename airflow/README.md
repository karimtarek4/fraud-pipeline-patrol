# 🚦 Airflow DAGs Orchestration

Welcome to the orchestration layer of the Fraud Pipeline Patrol project!
This directory contains all the Apache Airflow DAGs that automate and coordinate the end-to-end data pipeline for synthetic fraud detection.

---

## 🗺️ Pipeline Overview

The pipeline is composed of several modular DAGs, each responsible for a specific stage in the data lifecycle. The DAGs are connected via **Airflow Datasets**, where the completion of one DAG produces datasets that automatically trigger downstream DAGs, ensuring a robust and maintainable workflow.

```
[generate_and_partition_data_dag]
        │ (produces file datasets)
        ▼
[upload_to_minio_dag]
        │ (produces MinIO S3 dataset)
        ▼
[run_dbt_dag]
        │ (produces MinIO marts dataset)
        ▼
[ml_transaction_scoring_dag]
        │ (produces PostgreSQL fraud_alerts dataset)
        ▼
[alert_users_dag]
        │ (optionally triggers via TriggerDagRunOperator)
        ▼
[initialize_metabase_dag]
```

---

## 🔄 DAG Sequence & Dataset Dependencies

### 1. `generate_and_partition_data_dag`
- **Purpose:** Generates synthetic fraud data and partitions it for efficient processing.
- **Schedule:** Configurable via Airflow Variables (default: `*/1 * * * *`)
- **Produces Datasets:**
  - `file:///opt/airflow/data/processed/customers/`
  - `file:///opt/airflow/data/processed/merchants/`
  - `file:///opt/airflow/data/processed/transactions/`
  - `file:///opt/airflow/data/processed/login_attempts/`
- **Triggers:** `upload_to_minio_dag` via dataset production

---

### 2. `upload_to_minio_dag`
- **Purpose:** Uploads partitioned data to MinIO, maintaining directory structure.
- **Consumes Datasets:** All file datasets from `generate_and_partition_data_dag`
- **Produces Dataset:** `s3://minio:9000/fraud-data-processed/`
- **Triggers:** `run_dbt_dag` via dataset production

---

### 3. `run_dbt_dag`
- **Purpose:** Runs DBT models to transform and prepare data for scoring.
- **Consumes Dataset:** `s3://minio:9000/fraud-data-processed/`
- **Produces Dataset:** `s3://minio:9000/fraud-data-processed/marts/`
- **Logic:**
  - Installs DBT dependencies
  - Executes DBT transformations
- **Triggers:** `ml_transaction_scoring_dag` via dataset production

---

### 4. `ml_transaction_scoring_dag`
- **Purpose:** Scores transactions using ML models and generates fraud alerts.
- **Consumes Dataset:** `s3://minio:9000/fraud-data-processed/marts/`
- **Produces Dataset:** `postgresql://actualdata-postgres:5432/actualdata/public/fraud_alerts`
- **Logic:**
  - Runs the scoring script on transformed data
  - Saves fraud alerts to PostgreSQL
- **Triggers:** `alert_users_dag` via dataset production

---

### 5. `alert_users_dag`
- **Purpose:** Alerts customers identified in fraud alerts and optionally initializes Metabase.
- **Consumes Dataset:** `postgresql://actualdata-postgres:5432/actualdata/public/fraud_alerts`
- **Logic:**
  - Connects to PostgreSQL, fetches customers with fraud alerts
  - Simulates sending notifications via print statements
  - Uses branching logic to conditionally trigger Metabase initialization
- **Conditionally Triggers:** `initialize_metabase_dag` via `TriggerDagRunOperator` (if enabled via Variables)

---

### 6. `initialize_metabase_dag`
- **Purpose:** Sets up Metabase dashboards and database connections for fraud detection visualization.
- **Schedule:** Trigger by alert_users_dag dag
- **Logic:**
  - Runs the `initialize_metabase.py` script
  - Creates admin user, database connections, and imports dashboards/cards
  - Sets up fraud detection visualizations and analytics

---

## 📊 Dataset-Based Triggering Mechanism

The fraud detection pipeline uses **Airflow Datasets** to create automatic dependencies between DAGs. This approach provides several advantages:

### How It Works
- **Producers:** DAGs that generate or modify data declare `outlets` on their tasks
- **Consumers:** DAGs that depend on data declare `schedule=[dataset]` to automatically trigger when datasets are updated
- **Automatic Triggering:** When a task with dataset outlets completes successfully, all DAGs scheduled on those datasets are triggered