WITH source AS (
    SELECT * FROM {{ ref('raw_transaction') }}
),

cleaned AS (
    SELECT
        -- Identity fields
        TransactionID AS transaction_id,
        CustomerID AS customer_id,
        MerchantID AS merchant_id,
        
        -- Dates and timestamps
        Timestamp AS transaction_timestamp,
        
        -- Numeric fields
        NULLIF(TransactionAmount, 0) AS transaction_amount,
        
        -- Text fields with cleaning
        TRIM(COALESCE(DeviceID, 'Unknown')) AS device_id,
        TRIM(COALESCE(IP_Address, 'Unknown')) AS ip_address,
        TRIM(COALESCE(Channel, 'Unknown')) AS channel,

        -- Geographic coordinates
        Lat AS latitude,
        Lon AS longitude,
        
        -- System fields
        ingestion_date,
        
        -- Date components for analysis
        TimestampMonth AS transaction_month,
        EXTRACT(YEAR FROM Timestamp) AS transaction_year,
        EXTRACT(DOW FROM Timestamp) AS transaction_day_of_week,
        EXTRACT(HOUR FROM Timestamp) AS transaction_hour
        
    FROM source
),

final AS (
    SELECT
        *,
        -- Transaction pattern analysis
        CASE
            WHEN transaction_hour >= 0 AND transaction_hour < 6 THEN 'Night (12AM-6AM)'
            WHEN transaction_hour >= 6 AND transaction_hour < 12 THEN 'Morning (6AM-12PM)'
            WHEN transaction_hour >= 12 AND transaction_hour < 18 THEN 'Afternoon (12PM-6PM)'
            ELSE 'Evening (6PM-12AM)'
        END AS transaction_time_of_day,
        
        
        -- Additional fraud indicators
        (transaction_amount > 1000) AS is_high_value_transaction
    FROM cleaned
)

-- Final output with cleaned data and fraud detection indicators
SELECT 
    transaction_id,
    customer_id,
    merchant_id,
    transaction_timestamp,
    transaction_amount,
    device_id,
    ip_address,
    channel,
    latitude,
    longitude,
    ingestion_date,
    transaction_month,
    transaction_year,
    transaction_day_of_week,
    transaction_hour,
    transaction_time_of_day,
    is_high_value_transaction

FROM 
    final
