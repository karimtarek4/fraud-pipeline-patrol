{{ config(
    materialized='external',
    location='s3://fraud-data-processed/marts/v_login_attempt.parquet',
    format='parquet'
) }}

SELECT 
    -- Combine using surrogate key
    l.login_attempt_id,

    -- Foreign keys
    l.customer_id,

    -- Login details
    l.login_timestamp,
    l.is_success,
    l.login_month,
    l.login_year,
    l.login_day_of_week,
    l.login_hour,
    l.login_time_of_day,
    l.is_weekend_login,

    -- Customer risk indicators from dimension
    c.risk_level AS customer_risk_level,
    c.has_fraud_history AS customer_has_fraud_history,

    -- Login pattern metrics
    l.total_login_attempts,
    l.failed_login_attempts,
    l.weekend_login_attempts,
    l.night_login_attempts
FROM 
    {{ ref('fact_login_attempt') }} l
    LEFT JOIN {{ ref('dim_customer') }} AS c
        ON l.customer_id = c.customer_id