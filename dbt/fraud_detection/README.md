
# 🏗️ DBT Data Modeling Module

This directory contains all the data transformation logic, structured according to Kimball's dimensional modeling best practices.

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
---

## 🔄 Data Flow & Logic


1. **Landing Layer:**
   - Ingests raw data from MinIO (or S3) as external tables.
   - No transformation; just makes the data queryable.

2. **Staging Layer:**
   - Cleans and standardizes data types.
   - Handles missing values and basic data quality checks.

3. **Core Layer:**
   - Introduces fact tables.


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