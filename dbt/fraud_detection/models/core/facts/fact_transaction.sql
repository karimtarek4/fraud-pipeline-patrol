{{
  config(
    materialized='table',
    tags=['fact', 'core']
  )
}}

/*
  Enriched transactions model that extends the core fact table with dimension attributes
  and adds fraud detection metrics and indicators.
  
  This is where we add all the analytical features derived from dimension tables.
*/

WITH stg_transaction AS (
    SELECT *,
        -- Add any additional transaction attributes or derived metrics here
        CASE
            WHEN transaction_amount <= 100 THEN 'Low'
            WHEN transaction_amount <= 150 THEN 'Mid'
            ELSE 'High'
        END AS transaction_amount_tier,
        CASE
            WHEN transaction_amount > 150 THEN TRUE
            ELSE FALSE
        END AS is_high_value_transaction,
        -- Transaction time of day categorization using DuckDB's date_part
        CASE
            WHEN date_part('hour', transaction_timestamp) BETWEEN 0 AND 6 THEN 'Night (12AM-6AM)'
            WHEN date_part('hour', transaction_timestamp) BETWEEN 7 AND 11 THEN 'Morning (7AM-11AM)'
            WHEN date_part('hour', transaction_timestamp) BETWEEN 12 AND 17 THEN 'Afternoon (12PM-5PM)'
            ELSE 'Evening (6PM-11PM)'
        END AS transaction_time_of_day
     FROM {{ ref('stg_transaction') }}
),

dim_customers AS (
    SELECT * FROM {{ ref('dim_customer') }}
),

-- Join dimensions and calculate fraud metrics
enriched_transactions AS (
    SELECT
        -- Keys
        ft.transaction_id,
        ft.customer_id,
        ft.merchant_id,
        
        -- Transaction details from fact table
        ft.transaction_timestamp,
        ft.transaction_amount,
        ft.device_id,
        ft.ip_address,
        ft.channel,
        ft.latitude,
        ft.longitude,
        ft.transaction_time_of_day,
        ft.is_high_value_transaction,
       
        
        -- Calculate additional fraud risk indicators
        CASE
            WHEN c.risk_level = 'High' AND ft.is_high_value_transaction THEN TRUE
            WHEN c.has_fraud_history AND ft.transaction_amount > 500 THEN TRUE
            ELSE FALSE
        END AS has_elevated_fraud_risk,
        
        -- Distance calculation between transaction and customer home location
        CASE 
            WHEN c.home_latitude IS NOT NULL AND c.home_longitude IS NOT NULL AND 
                 ft.latitude IS NOT NULL AND ft.longitude IS NOT NULL
            THEN SQRT(POW(c.home_latitude - ft.latitude, 2) + POW(c.home_longitude - ft.longitude, 2))
            ELSE NULL
        END AS distance_from_home
    FROM 
        stg_transaction ft
    LEFT JOIN 
        dim_customers c ON ft.customer_id = c.customer_id
)

SELECT
    -- Keys
    transaction_id,
    customer_id,
    merchant_id,
    
    -- Transaction details from fact table
    transaction_timestamp,
    transaction_amount,
    device_id,
    ip_address,
    channel,
    latitude,
    longitude,
    transaction_time_of_day,
    is_high_value_transaction,

    -- Additional fraud risk indicators
    has_elevated_fraud_risk,

    -- Distance calculation between transaction and customer home location
    distance_from_home
    
FROM 
    enriched_transactions
