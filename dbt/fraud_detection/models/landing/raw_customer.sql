WITH base AS (
    SELECT 
        CustomerID,
            AccountCreationDate,
            Age,
            AvgTransactionAmount,
            PastFraudCount,
            HomeDevice,
            HomeIP,
            HomeLat,
            HomeLon,
            ingestion_date,
            AccountCreationMonth
    FROM {{ source('fraud_data', 'customers') }}
)

SELECT * FROM base