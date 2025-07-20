# 🚦 Airflow DAGs Orchestration

Welcome to the orchestration layer of the Fraud Pipeline Patrol project!
This directory contains all the Apache Airflow DAGs that automate and coordinate the end-to-end data pipeline for synthetic fraud detection.

---

## 🗺️ Pipeline Overview

The pipeline is composed of several modular DAGs, each responsible for a specific stage in the data lifecycle. The DAGs are connected in a downstream sequence, where the completion of one triggers the next, ensuring a robust and maintainable workflow.

```
[generate_and_partition_data_dag]
            │
            ▼
   [upload_to_minio_dag]
            │
            ▼
        [run_dbt_dag]
            │
            ▼
 [ml_transaction_scoring_dag]
            │
            ▼
    [alert_users_dag]
            │
            ▼
[visualize_alert_data_dag]
```

---

## 🔄 DAG Sequence & Dependencies

### 1. `generate_and_partition_data_dag`
- **Purpose:** Generates synthetic fraud data and partitions it for efficient processing.
- **Logic:**
  - Waits for all other DAGs to finish before starting (to avoid resource conflicts).
  - Runs scripts to generate and partition data.
  - **Triggers:** `upload_to_minio_dag` upon completion.

---

### 2. `upload_to_minio_dag`
- **Purpose:** Uploads partitioned data to MinIO, maintaining directory structure.
- **Logic:**
  - Executes a script to upload all processed data.
  - **Triggers:** `run_dbt_dag` after upload is complete.

---

### 3. `run_dbt_dag`
- **Purpose:** Runs DBT models to transform and prepare data for scoring.
- **Logic:**
  - Installs DBT dependencies.
  - Executes DBT transformations.
  - **Triggers:** `ml_transaction_scoring_dag` after DBT run.

---

### 4. `ml_transaction_scoring_dag`
- **Purpose:** Scores transactions using the latest models and logic.
- **Logic:**
  - Runs the scoring script.
  - **Triggers:** `alert_users_dag` after scoring is complete.

---

### 5. `alert_users_dag`
- **Purpose:** Alerts customers identified in fraud alerts and initiates visualization.
- **Logic:**
  - Connects to the database, fetches customers with fraud alerts, and simulates sending notifications.
  - **Triggers:** `visualize_alert_data_dag` to generate updated visualizations.

## ⏳ Orchestration Logic

- **Downstream Triggers:** Each DAG (except the last) triggers the next DAG using Airflow’s `TriggerDagRunOperator`.
- **Resource Management:** The first DAG waits for all other DAGs to finish before starting, ensuring no resource contention.
- **Manual & Scheduled Runs:** The initial data generation DAG can be scheduled (e.g., every minute), while others are typically triggered downstream.

---

## 🎯 Purpose

This modular DAG structure:
- Promotes separation of concerns and maintainability.
- Allows for easy debugging and monitoring of each pipeline stage.
- Enables flexible scaling and future extension of the pipeline.

---


## 📝 Notes

- All DAGs are designed to run in a Dockerized Airflow environment.
- Environment variables and script paths are configurable for flexibility.
- Each DAG is documented in its own file for further details.
