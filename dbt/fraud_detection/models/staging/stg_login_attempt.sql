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
        ingestion_date

    FROM source
)

SELECT 
    customer_id,
    login_timestamp,
    is_success,
    ingestion_date
FROM 
    cleaned
