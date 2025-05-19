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
),

final AS (
    SELECT
        *,
        -- Merchant risk categorization based on risk score
        CASE 
            WHEN merchant_risk_score >= 0.7 THEN 'High Risk'
            WHEN merchant_risk_score >= 0.4 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS merchant_risk_category,
        
        -- Additional business metrics
        (merchant_risk_score >= 0.7) AS is_high_risk_merchant
    FROM cleaned
)

-- Final output with all cleaned fields and derived risk metrics
SELECT 
    merchant_id,
    merchant_name,
    merchant_category,
    merchant_risk_score,
    ingestion_date,
    merchant_risk_category,
    is_high_risk_merchant
FROM 
    final
