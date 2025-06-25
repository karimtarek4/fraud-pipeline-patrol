
# 🛡️ Fraud Pipeline Patrol — Modular, Production-Inspired Fraud Detection

A modular, end-to-end fraud detection pipeline simulating real-world data workflows using Airflow, dbt, Python, and modern data tools. This project demonstrates advanced analytics engineering, orchestration, and modeling skills—built to impress and inspire!

---

## 🎯 Project Goal

Build a robust, production-style data pipeline that detects fraudulent financial transactions using engineered features and rule-based logic. This project showcases:

- Automated data generation, ingestion, and partitioning
- Dimensional modeling and transformation with dbt (Kimball methodology)
- Modular, explainable risk scoring in Python
- Alerting, notification, and rich visualizations
- Fully dockerized, reproducible development environment

---

## 🧱 Tech Stack

| Tool       | Role                                 |
|------------|--------------------------------------|
| Airflow    | Pipeline orchestration               |
| dbt        | Dimensional modeling & transformation|
| Python     | Scoring logic & alerting             |
| MinIO      | S3-compatible object storage         |
| DuckDB     | Fast analytics & Parquet processing  |
| Postgres   | Analytical storage                   |
| Matplotlib/Seaborn | Visualization & reporting    |
| Docker     | Reproducibility & deployment         |

---

## 🗂️ Project Structure

```
fraud-pipeline-patrol/
│
├── airflow/      # Airflow DAGs & orchestration
├── dbt/          # dbt project (core, landing, staging, marts)
├── scoring/      # Python scoring logic
├── data/         # Raw, processed, and results data
├── docker/       # Dockerfiles and compose
├── visualizations/ # Python-generated charts
├── notebooks/    # Optional EDA
└── README.md     # This file
```

---

## 🔄 Pipeline Flow

### 1. **Synthetic Data Generation & Ingestion**
- Airflow DAGs generate rich, synthetic data (customers, merchants, transactions, logins)
- Data is partitioned and uploaded to MinIO (S3-compatible object storage)

### 2. **Dimensional Modeling (dbt)**
- Data is modeled using Kimball's dimensional modeling techniques:
  - **Core:** Raw ingested data
  - **Landing:** Cleaned, type-cast, and standardized
  - **Staging:** Business logic, feature engineering, SCD2, surrogate keys
  - **Marts:** Star schema (facts & dimensions) for analytics and scoring
- Marts are exported as Parquet files for downstream use

### 3. **Scoring (Python)**
- Reads enriched marts directly from MinIO using DuckDB
- Applies modular, rule-based scoring logic:
  - Failed logins, geo mismatch, high-risk merchant/customer, outlier detection, odd hours, etc.
- Flags risky transactions and writes alerts to both Parquet and Postgres

### 4. **Alerting & Visualization**
- Alerts are used to notify users and generate visual reports
- Visualizations are created using Python libraries (Matplotlib, Seaborn) and saved as images in the `visualizations/` directory
- Visuals include:
  - Top 10 risky customers
  - Most common fraud alert flags
  - Alerts over time
  - Risk score distribution
- These help monitor fraud trends and system performance
---

## 🚧 Next Steps & Improvements

- Add automated tests for each module (unit, integration, and data quality)
- Expand scoring logic with machine learning models for adaptive fraud detection
- Build a simple web dashboard (e.g., Streamlit) for interactive monitoring
- Parameterize and document environment setup for easier onboarding
- Add CI/CD for automated deployment and testing
- Enhance alerting (e.g., real email/SMS notifications)
- Improve data generation realism (simulate more fraud scenarios)

---

---

## � Orchestration Logic

- Modular Airflow DAGs orchestrate each stage, triggering downstream DAGs upon completion
- Resource management ensures no conflicts and smooth, sequential execution
- Each module is independently testable and extensible

---

## 🌟 Why This Project Stands Out

- **Production-inspired:** Mirrors real-world data engineering best practices
- **Kimball modeling:** Clean, analytics-ready marts for BI and ML
- **Explainable scoring:** Transparent, auditable fraud detection logic
- **Modular & extensible:** Each component can be swapped, scaled, or extended
- **Beautiful dashboards:** End-to-end visibility from raw data to business insights

---

## 👤 Author

**Karim Tarek** — Data & Analytics Engineer  
_Seeking Staff Analytics Engineering roles_  
📫 [LinkedIn](https://www.linkedin.com/in/karimtarek)


