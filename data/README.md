# 📁 `data/` Directory

The `data/` directory is the **source of truth** for all raw and processed data used in the fraud detection pipeline. It contains:

---

## 1. `generate_synthetic_fraud_data.py`

A Python script that **generates a rich synthetic dataset** for the project. When executed, it:

* Creates **customer profiles** with SCD2 fields and behavioral baselines.
* Builds a **merchant table** with risk scores per category.
* Produces **transaction records** that include:

  * Realistic timing (exponential inter-arrival + bursts)
  * Rule-based features (amount around baseline, device/IP consistency, geolocation drift)
  * Metadata (`batch_id`, `ingestion_date`) for incremental loads
* Extracts **login attempts** into a separate table for modeling authentication events.
* Writes out **Parquet** files (with CSV fallback) under `data/raw/`:

  * `customers.parquet` (or `.csv`)
  * `merchants.parquet` (or `.csv`)
  * `transactions.parquet` (or `.csv`)
  * `login_attempts.parquet` (or `.csv`)

**Usage:**

```bash
pip install pandas numpy pyarrow
python data/generate_synthetic_fraud_data.py
```

---

## 2. `data/raw/`

After running the script, this folder will contain your **raw data** artifacts:

* **Customer** table: foundational dimension for modeling (with SCD2 candidates).
* **Merchant** table: lookup dimension enriched with risk scores.
* **Transaction** facts: base events for ingestion and dbt staging.
* **Login Attempts** facts: separate authentication event logs.

Your **Airflow ingestion DAG** and **dbt sources** will point to these files as the starting point of the pipeline.

---

## 3. `data/processed/` (optional)

Once you begin staging and transforming data (e.g., via Airflow or dbt), use this folder to store **intermediate outputs**:

* Cleaned and enriched tables ready for analytics models.
* Partitioned Parquet by date if desired.

---

This structure ensures a clear separation between raw inputs and transformed outputs, facilitating incremental loads, reproducibility, and robust testing throughout your pipeline.
