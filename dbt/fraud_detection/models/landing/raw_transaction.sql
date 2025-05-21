WITH base AS (
    SELECT 
        TransactionID,
        CustomerID,
        Timestamp,
        TransactionAmount,
        DeviceID,
        IP_Address,
        Lat,
        Lon,
        Channel,
        MerchantID,
        current_localtimestamp() as ingestion_date
    FROM {{ source('fraud_data', 'transactions') }}
)

SELECT * FROM base