{{
  config(
    materialized='table',
    tags=['staging', 'cleaned']
  )
}}

WITH source AS (
    SELECT * FROM {{ ref('raw_login_attempt') }}
),

cleaned AS (
    SELECT
        -- Primary keys and IDs
        CustomerID AS customer_id,
        
        -- Dates and timestamps
        LoginTimestamp AS login_timestamp,
        
        -- Boolean fields
        Success AS is_success,
        
        -- Metadata and system fields
        ingestion_date,
        
        -- Date components for analysis
        LoginTimestampMonth AS login_month,
        EXTRACT(YEAR FROM LoginTimestamp) AS login_year,
        EXTRACT(DOW FROM LoginTimestamp) AS login_day_of_week,
        EXTRACT(HOUR FROM LoginTimestamp) AS login_hour,

    FROM source
),

final AS (
    SELECT
        *,
        -- Login pattern analysis (example derived fields)
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
    FROM cleaned
)

SELECT 
    customer_id,
    login_timestamp,
    is_success,
    ingestion_date,
    login_month,
    login_year,
    login_day_of_week,
    login_hour,
    login_time_of_day,
    is_weekend_login
FROM 
    final
