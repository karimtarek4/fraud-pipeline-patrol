WITH source AS (
    SELECT * FROM {{ ref('raw_merchant') }}
),

cleaned AS (
    SELECT
        -- Identity fields
        MerchantID AS merchant_id,

        -- Business information
        TRIM(COALESCE(MerchantName, 'Unnamed Merchant')) AS merchant_name,
        TRIM(COALESCE(Category, 'Uncategorized')) AS merchant_category,

        -- Risk metrics
        COALESCE(MerchantRiskScore, 0.5) AS merchant_risk_score,

        -- System fields
        ingestion_date,
    FROM source
)

-- Final output with all cleaned fields and derived risk metrics
SELECT
    merchant_id,
    merchant_name,
    merchant_category,
    merchant_risk_score,
    ingestion_date
FROM
    cleaned
