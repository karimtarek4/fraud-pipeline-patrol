WITH base AS (
        SELECT 
            CustomerID,
            AccountCreationDate,
            Age,
            -- @ To be calculated as metric in fact_transaction
            -- AvgTransactionAmount,
            PastFraudCount,
            HomeDevice,
            HomeIP,
            HomeLat,
            HomeLon,
            current_localtimestamp() AS ingestion_date
        FROM 
            {{ source('fraud_data', 'customers') }}
)

SELECT * FROM base