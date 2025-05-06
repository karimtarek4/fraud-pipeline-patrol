# 🛡️ Fraud Detection Pipeline — Rule-Based, Modular & Production-Inspired
A modular fraud detection pipeline simulating real-world data workflows using Airflow, dbt, and Python. Includes rule-based scoring, alerting, and dashboards. Built for analytics engineers to showcase orchestration, modeling, and platform skills.


This project simulates a real-world fraud detection pipeline, focusing on **Analytics Engineering**, **Data Orchestration**, and **Reproducible Infra**.

## 🎯 Project Goal

Build an end-to-end data pipeline that detects fraudulent financial transactions using engineered features and rule-based logic. This project showcases:

- Data ingestion with Airflow
- Modeling and testing with dbt
- Risk scoring in Python
- Alerting and visualization
- Dockerized development environment

---

## 🧱 Tech Stack

| Tool       | Role                            |
|------------|---------------------------------|
| Airflow    | Pipeline orchestration          |
| dbt        | Modeling + testing + semantics  |
| Python     | Scoring logic + alerting        |
| MinIO      | Local S3-compatible object store|
| Postgres   | Analytical storage               |
| Metabase   | Dashboards & reporting           |
| Docker     | Reproducibility & deployment     |

---

## 🗂️ Project Structure
fraud-detection-pipeline/
│
├── data/ # Source and sample data
├── dags/ # Airflow DAGs
├── dbt/ # dbt project files
├── scoring/ # Scoring logic
├── docker/ # Dockerfiles and compose
├── metabase/ # Dashboard setup or exports
├── notebooks/ # Optional EDA
└── README.md # This file

## 🧪 Pipeline Flow

### 1. **Data Layer**
- Download or generate base data
- Extend with synthetic rows
- Convert to Parquet format
- Upload to MinIO bucket (`raw/`)

### 2. **Ingestion DAG**
- Airflow fetches raw Parquet files
- Loads into DuckDB or Postgres

### 3. **Modeling (dbt)**
- Stage, clean, and enrich tables
- Create reusable marts:
    - `v_transactions`
    - `daily_user_summary`
    - `risk_exposures`
- Add tests and metrics via Semantic Layer

### 4. **Scoring (Python)**
- Read enriched tables
- Apply modular rules:
    - Transaction amount
    - Merchant risk
    - Failed login attempts
    - Account age, anomaly score, etc.
- Write `fraud_alerts` table
- Send notifications (email/Slack)

### 5. **Visualization (Metabase)**
- Connect to Postgres
- Dashboards:
    - High-risk accounts
    - Fraud trend over time
    - Merchant/category heatmaps
    - Time-to-resolution metrics

---

## 🚀 Deployment Plan

- All components run via `docker-compose`
- Airflow schedules ingestion + scoring
- Python scoring logic containerized separately
- Bonus: deploy scoring job as Kubernetes CronJob

---

## ✅ Status Tracker

| Task                    | Status      |
|-------------------------|-------------|
| Data download/prep      | ⬜️ Not started
| Airflow DAG             | ⬜️ Not started
| dbt models              | ⬜️ Not started
| Scoring logic (Python)  | ⬜️ Not started
| Docker setup            | ⬜️ Not started
| Metabase dashboards     | ⬜️ Not started

---

## 👤 Author

**Karim Tarek** — Data & Analytics Engineer  
_Seeking Staff Analytics Engineering roles_  
📫 [LinkedIn](https://www.linkedin.com/in/karimtarek)


