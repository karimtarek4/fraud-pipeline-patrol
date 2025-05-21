WITH base AS (
    SELECT
        MerchantID,
        MerchantName,
        Category,
        MerchantRiskScore,
        local_timestamp() ingestion_date
    FROM {{ source('fraud_data', 'merchants') }}
)

SELECT * FROM base