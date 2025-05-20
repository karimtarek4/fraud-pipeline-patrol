{{
  config(
    materialized='table',
    tags=['fact', 'core']
  )
}}

/*
  Login attempts fact table that links to the customer dimension
  and provides login pattern analysis for fraud detection.
*/

WITH stg_login_attempt AS (
    SELECT * FROM {{ ref('stg_login_attempt') }}
),

dim_customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

add_columns AS (
    SELECT
        stg_login_attempt.*,
        EXTRACT(MONTH FROM login_timestamp) AS login_month,
        EXTRACT(YEAR FROM login_timestamp) AS login_year,
        EXTRACT(DOW FROM login_timestamp) AS login_day_of_week,
        EXTRACT(HOUR FROM login_timestamp) AS login_hour,
        CASE
            WHEN login_hour >= 0 AND login_hour < 6 THEN 'Night (12AM-6AM)'
            WHEN login_hour >= 6 AND login_hour < 12 THEN 'Morning (6AM-12PM)'
            WHEN login_hour >= 12 AND login_hour < 18 THEN 'Afternoon (12PM-6PM)'
            ELSE 'Evening (6PM-12AM)'
        END AS login_time_of_day,
        
        CASE
            WHEN login_day_of_week IN (0, 6) THEN TRUE  -- 0=Sunday, 6=Saturday
            ELSE FALSE
        END AS is_weekend_login
    FROM stg_login_attempt
),

-- Calculate login metrics by customer
customer_login_metrics AS (
    SELECT
        customer_id,
        COUNT(*) AS total_login_attempts,
        SUM(CASE WHEN is_success = FALSE THEN 1 ELSE 0 END) AS failed_login_attempts,
        SUM(CASE WHEN is_weekend_login = TRUE THEN 1 ELSE 0 END) AS weekend_login_attempts,
        SUM(CASE WHEN login_time_of_day = 'Night (12AM-6AM)' THEN 1 ELSE 0 END) AS night_login_attempts
    FROM add_columns
    GROUP BY customer_id
)

SELECT
    -- Combine using surrogate key
    {{ dbt_utils.generate_surrogate_key(['l.customer_id', 'l.login_timestamp']) }} AS login_attempt_id,
    
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
    
    -- Login pattern metrics
    clm.total_login_attempts,
    clm.failed_login_attempts,
    clm.weekend_login_attempts,
    clm.night_login_attempts

FROM 
    add_columns l
LEFT JOIN
    customer_login_metrics clm
    ON l.customer_id = clm.customer_id