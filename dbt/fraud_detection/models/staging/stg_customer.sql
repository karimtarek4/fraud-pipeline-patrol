WITH source AS (
    SELECT * FROM {{ ref('raw_customer') }}
),

cleaned AS (
    SELECT
        -- Identity fields
        CustomerID AS customer_id,

        -- Date fields
        AccountCreationDate AS account_creation_date,

        -- Demographic information
        Age AS age,

        -- Metrics
        COALESCE(PastFraudCount, 0) AS past_fraud_count,

        -- Device and location info
        TRIM(COALESCE(HomeDevice, 'Unknown')) AS home_device,
        TRIM(HomeIP) AS home_ip,  -- Added missing AS keyword
        HomeLat AS home_latitude,
        HomeLon AS home_longitude,

        -- System fields
        ingestion_date
    FROM source
)

-- Final output with all cleaned and derived fields
SELECT
-- list all columns from previous ctes with addition one by one
    customer_id,
    account_creation_date,
    age,
    past_fraud_count,
    home_device,
    home_ip,
    home_latitude,
    home_longitude
 FROM
    cleaned
