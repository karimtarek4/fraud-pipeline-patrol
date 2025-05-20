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
        ingestion_date
        

        
    FROM source
),

final AS (
    SELECT
        *
    FROM 
        cleaned
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
    ingestion_date

FROM 
    final
