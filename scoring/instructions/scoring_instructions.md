1. Context and Goals
This project is a portfolio-grade, modular fraud analytics pipeline intended to showcase Staff-level analytic/data engineering skills. The pipeline uses Airflow, DBT, MinIO, DuckDB/Postgres, and Metabase, with synthetic data representing financial transactions and authentication events. The key business logic now needed is the Scoring & Alerting phase, which will demonstrate:
System orchestration and modularity


Extensible, testable code structure


Realistic, cross-domain feature engineering (from both payments and login data)


End-to-end automation and observability


The focus is on clean, production-grade engineering and documentation, not on developing sophisticated ML models for scoring. The scoring logic should be clear, interpretable, and extensible—demonstrating how such systems can be improved or scaled in real-world use.

2. Current Architecture (Summary)
Raw data (transactions, logins, etc.) generated, partitioned, and uploaded to MinIO.


DBT transforms data into marts: v_transactions and v_login_attempts.


Airflow DAGs orchestrate generation, ingestion, transformation, and (to be added) scoring.


Metabase (upcoming) will visualize alerts and trends.


Directory Structure: Follows best practices with scoring/, airflow/dags/, and dbt/models/ as key locationsProject Structure Detailed Implementation.



3. High-Level Tasks for Scoring & Alerting
A. Input & Output
Input: v_transactions (primary), with enrichment from v_login_attempts (authentication context)


Output: fraud_alerts table (contains transaction_id, risk_score, flags, timestamp, notified, etc.)


Notifications: Trigger Slack/email/print alert if risk_score exceeds threshold


B. Pipeline Flow
Triggered by Airflow after DBT transformations complete for each batch.


Scoring script loads transactions, enriches with login signals, computes features and risk scores, writes alerts, and triggers notifications as needed.


Designed for extensibility and clarity, so future ML models can be slotted in with minimal change.



4. Scoring Algorithm Construction Guidelines
a) Feature Engineering
Use both marts:


From v_transactions: transaction amount, merchant, location, device, etc.


From v_login_attempts: failed logins, recent device/IP, location, time deltas.


Enrich each transaction with authentication context:


E.g., number of failed logins in last 24h, geo mismatch, device mismatch, time since last login.


b) Scoring Logic
Start with interpretable, rule-based logic (e.g., z-score for amount, count of failed logins, device/geo anomaly).


Assign risk_score based on additive or weighted rules, e.g.:


+1 for >3 failed logins before transaction


+2 for login from new country/device before transaction


+1 if transaction is a statistical outlier for user


Flags: Set flags for each triggered rule (e.g., “FAILED_LOGIN”, “GEO_MISMATCH”).


Threshold: If risk_score ≥ threshold, trigger alert/notification.


c) Implementation Pattern
Modular, testable code:


Isolate feature extraction, scoring, and alerting functions.


Write docstrings and comments on extensibility (where to insert ML/advanced rules in the future).


Use configuration/constants for thresholds and scoring weights.


Efficient data access:


Option 1: Join marts in-memory (pandas/duckdb) per batch in the scoring script.


Option 2: Pre-join login signals into v_transactions via DBT (recommended for reusability).


Logging & observability: Print/log scored batch summaries, errors, and notification results.


d) Orchestration & Integration
Airflow DAG:


Sensor waits for DBT completion.


PythonOperator runs scoring module.


Notification handled in Python or Airflow notification operator.


e) Documentation and Communication
README and code docstrings should:


Clearly explain the logic and where to extend/replace rules with ML.


Include a section (“Cross-Domain Feature Engineering: Transactions + Auth Signals”).


Explain tradeoffs: pipeline engineering focus, rule-based for demo, ML-ready design.



5. Portfolio-Grade Focus
Emphasize system design, orchestration, and analytic feature engineering over model sophistication.


Demonstrate analytic creativity by crossing transaction and login/authentication signals.


Show extensibility by making it clear how the scoring logic could be swapped out or extended with ML in production.


Highlight traceability: from data generation → transformation → scoring → alerting → visualization.



