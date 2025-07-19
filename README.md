![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![dbt](https://img.shields.io/badge/dbt-%23FF694B.svg?logo=dbt&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-2.8.1-blue?logo=apache-airflow)
![Docker](https://img.shields.io/badge/Docker-Desktop-blue?logo=docker)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green?logo=github)
![Security](https://img.shields.io/badge/Security-Bandit%20%7C%20Safety-red?logo=security)
![Code Quality](https://img.shields.io/badge/Code%20Quality-Black%20%7C%20Flake8%20%7C%20MyPy-blue?logo=code-review)

A modular, end-to-end fraud detection pipeline simulating real-world data workflows using Airflow, dbt, Python, and modern data tools. This project demonstrates advanced analytics engineering, orchestration, and modeling skills—built to impress and inspire!

---

## 🎯 Project Goal

Build a robust, production-style data pipeline that detects fraudulent financial transactions using engineered features and rule-based logic. This project showcases:

- Automated data generation, ingestion, and partitioning
- Dimensional modeling and transformation with dbt (Kimball methodology)
- Hybrid rule-based + ML risk scoring in Python
- Alerting and auto-generated Metabase dashboards
- Fully dockerized, reproducible development environment
- CI/CD Pipeline

---

## 🧱 Tech Stack

| Tool              | Role                                       |
|-------------------|--------------------------------------------|
| Airflow           | Pipeline orchestration with Datasets & Variables |
| dbt               | Dimensional modeling & transformation      |
| Python            | Scoring logic & alerting                   |
| MinIO             | S3-compatible object storage               |
| DuckDB            | Fast analytics & Parquet processing        |
| Postgres          | Analytical storage                         |
| Metabase          | Data visualization and dashboarding        |
| Docker            | Reproducibility & deployment               |

---


## 🧭 Architecture Diagram

![Architecture](assets/architecture_diagram.png)

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

### 3. **Scoring (Python + ML)**

- Reads enriched marts directly from MinIO using DuckDB
- Applies **hybrid fraud detection logic**, combining:

  #### 🔍 Rule-Based Scoring:
  - Flags suspicious behavior using domain-driven rules:
    - Failed login attempts
    - Geo-location mismatch
    - Night/weekend login patterns
    - High-risk merchants or customers
    - Z-score outliers in transaction amount
  - Produces a `risk_score` and triggers one or more `flags`

  #### 🤖 Machine Learning Scoring:
  - Trained **Random Forest Classifier** on weak labels from rule-based scores
  - Uses features like:
    - `failed_logins_24h`, `geo_mismatch`, `night_login`, `is_high_risk_merchant`, `transaction_amount`
  - Achieves:
    - **Accuracy:** 0.99
    - **Precision:** 0.97
    - **Recall:** 0.97
    - **F1 Score:** 0.97
  PS: Please refer to /scoring/fraud_model_building.ipynb for a walkthrough of how the model was developed.

- **Scoring Output:**
  - `fraud_alerts` table containing: `transaction_id`, `risk_score`, `flags`, `ml_score`, `label`
  - Alerts saved to both **Parquet** and **Postgres**

---


### 4. **Visualization (Metabase) Script**
  - Launches a Metabase instance (if not running)
  - Initializes Metabase using `initialize_metabase.py`, which:
    - Skips the welcome wizard
    - Creates admin account
    - Adds Postgres DB connection
    - Imports dashboards/cards from JSON in `metadata/`
- Metabase dashboards include:
  - Top risky customers
  - Most common fraud flags
  - Alerts over time
  - Risk score distribution
- Dashboards are updated on each DAG run via automatic refresh


## 5. Testing & Quality Assurance

This project includes a comprehensive test suite with **44 tests** across multiple categories to ensure pipeline reliability and correctness:

| Test Category | Files | Tests | Coverage |
|---------------|-------|-------|----------|
| **Unit Tests** | 2 | 6 | Database connections & helpers |
| **Script Tests** | 1 | 7 | Data generation & file operations |
| **DAG Tests** | 2 | 31 | Airflow pipeline validation |

### Key Testing Features:
- **Automated Test Runner**: `python run_all_tests.py` - detects environments and runs all tests
- **Environment Detection**: Automatically finds the correct pytest with Airflow support
- **Comprehensive Coverage**: Tests database connections, data generation logic, and complete DAG pipeline validation
- **CI/CD Ready**: Proper exit codes and reporting for continuous integration

### Quick Local Test Commands:
```bash
# Run all tests with automatic environment detection
python run_all_tests.py
```

### 6. CI/CD Pipeline (GitHub Actions)

Our **4-stage enterprise CI/CD pipeline** ensures code quality, security, and reliability:

| Stage | Purpose | Tools | Validation |
|-------|---------|-------|------------|
| **🏗️ Docker Build** | Container integrity | Docker, BuildKit | Multi-platform builds |
| **🧪 Test Suite** | Code reliability | pytest, custom runner | 44+ automated tests |
| **✈️ Airflow Validation** | Pipeline integrity | Airflow DAG parsing | Syntax & import validation |
| **📊 dbt Validation** | Model integrity | dbt compile, test | SQL compilation & tests |

---


### 7⚡ Makefile Commands

We've created a comprehensive Makefile for **effortless project interaction**:

```bash
# 🚀 Quick Start
make setup              # Full development environment setup
make install-dev        # Install all dependencies
make setup-hooks        # Configure pre-commit hooks

# 🧪 Testing & Quality
make test              # Run all 44+ tests
make lint              # Run linting checks
make format            # Auto-format code
make security          # Security vulnerability scan
make pre-commit        # Run all quality checks

# 📋 Help
make help              # Show all available commands
```

## 🌟 Why This Project Stands Out

- **Production-inspired:** Mirrors real-world data engineering best practices
- **Data-Driven Architecture:** Airflow Datasets ensure reliable, event-driven pipeline execution
- **Operational Excellence:** Variables provide zero-downtime configuration and feature toggles
- **Intelligent Branching:** Dynamic workflow paths based on runtime conditions and feature flags
- **Kimball modeling:** Clean, analytics-ready marts for BI and ML
- **Hybrid Scoring:** Combines transparent rules with adaptive ML logic
- **Self-building dashboards:** Metabase is fully automated and initialized via Airflow
- **Modular & extensible:** Each component can be swapped, scaled, or extended
- **DevOps & CI/CD Excellence**  4-stage GitHub Actions workflow with comprehensive validation

---

## 👤 Author

**Karim Tarek** — Data & Analytics Engineer
📫 [LinkedIn](https://www.linkedin.com/in/karimtarek)
