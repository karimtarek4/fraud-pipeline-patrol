WITH base AS (
    SELECT 
        CustomerID,
        LoginTimestamp,
        Success,
        ingestion_date,
        LoginTimestampMonth
    FROM {{ source('fraud_data', 'login_attempts') }}
)

SELECT * FROM base