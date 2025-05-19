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
        PastFraudCount,
        MerchantID,
        MerchantName,
        MerchantCategory,
        MerchantRiskScore,
        ingestion_date,
        TimestampMonth
    FROM {{ source('fraud_data', 'transactions') }}
)

SELECT * FROM base