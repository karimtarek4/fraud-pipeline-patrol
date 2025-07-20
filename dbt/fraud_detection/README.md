
# 🏗️ DBT Data Modeling Module

Welcome to the DBT (Data Build Tool) module of the Fraud Pipeline Patrol project! This directory contains all the data transformation logic, structured according to Kimball's dimensional modeling best practices, to enable robust, scalable, and analytics-ready data for fraud detection and scoring.

---

## 📦 Project Structure

```
dbt/
  fraud_detection/
    dbt_project.yml
    models/
      core/        # Core source tables (raw ingested data)
      landing/     # Cleaned and lightly transformed data
      staging/     # Business logic, denormalization, surrogate keys
      marts/       # Star schema: facts & dimensions for analytics
    ...
```

- **core/**: Contains the raw, ingested data as-is from the data lake or warehouse. No business logic applied.
- **landing/**: Applies initial cleaning, type casting, and basic transformations to raw data. Prepares for further modeling.
- **staging/**: Implements business rules, joins, and denormalization. Surrogate keys and slowly changing dimensions (SCD) are handled here. This is where Kimball's techniques shine: conformed dimensions, fact tables, and SCDs are built.
- **marts/**: The analytics-ready layer. Contains star schema models (fact and dimension tables) designed for downstream analytics, scoring, and reporting.

---

## 🧩 Dimensional Modeling Approach

This module is designed following the principles of Kimball's dimensional modeling:
- **Star Schema:** Fact tables (e.g., transactions, login attempts) are at the center, surrounded by dimension tables (e.g., customer, merchant).
- **Conformed Dimensions:** Shared dimensions (like customer) are consistent across marts.
- **Surrogate Keys:** Used for joining facts and dimensions, supporting SCD2 for historical tracking.
- **Slowly Changing Dimensions (SCD):** Customer and merchant profiles track changes over time, enabling point-in-time analysis.
- **Business Logic in Staging:** All business rules, feature engineering, and denormalization are handled in the staging layer, keeping marts clean and analytics-ready.

---

## 🔄 Data Flow & Logic

1. **Core Layer:**
   - Ingests raw data from MinIO (or S3) as external tables.
   - No transformation; just makes the data queryable.

2. **Landing Layer:**
   - Cleans and standardizes data types.
   - Handles missing values and basic data quality checks.

3. **Staging Layer:**
   - Applies business logic, joins, and feature engineering.
   - Builds surrogate keys and SCD2 fields.
   - Prepares fact and dimension tables for analytics.

4. **Marts Layer:**
   - Exposes star schema models for analytics and scoring.
   - Fact tables (e.g., `v_transaction`, `v_login_attempt`) are joined with dimensions for rich, denormalized records.
   - These marts are exported as Parquet files to S3/MinIO for downstream consumption.

---

## 🌟 Marts: Analytics-Ready Models

### `v_transaction`
- Combines transaction facts with customer and merchant dimensions.
- Includes engineered features (risk scores, distance from home, high-risk flags).
- Used as the primary input for the scoring pipeline (see Airflow DAGs: `ml_transaction_scoring_dag`).

### `v_login_attempt`
- Combines login attempt facts with customer risk attributes.
- Includes login pattern metrics and risk indicators.
- Supports authentication risk modeling and monitoring.

---

## 🚦 Integration with the Pipeline

- The marts are exported as Parquet files to S3/MinIO, making them available for the next stage in the pipeline.
- The Airflow DAGs trigger the DBT models after data upload, and then trigger the ml scoring DAG to use these marts for fraud detection.
- This modular, layered approach ensures data quality, traceability, and flexibility for analytics and machine learning.

---

## 📝 Why Dimensional Modeling?

- **Clarity:** Star schemas make analytics and reporting intuitive.
- **Performance:** Denormalized marts are fast to query and ideal for BI tools and ML pipelines.
- **Maintainability:** Each layer has a clear purpose, making the project easy to extend and debug.
- **Historical Analysis:** SCD2 and surrogate keys enable point-in-time and trend analysis, critical for fraud detection.

---
