{{
  config(
    materialized='table',
    tags=['dim', 'core']
  )
}}

/*
  Merchant dimension table that provides a comprehensive view of merchants
  including their risk categorization, business categories, and derived metrics.
*/

WITH stg_merchant AS (
    SELECT * FROM {{ ref('stg_merchant') }}
),

-- Add any additional merchant metrics or aggregations here
infer_columns AS (
    SELECT
        stg_merchant.*,
        -- flags
        (merchant_risk_score >= 0.7) AS is_high_risk_merchant,
        -- Derived risk classification
        CASE 
            WHEN merchant_risk_score >= 0.7 THEN 'High Risk'
            WHEN merchant_risk_score >= 0.4 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS merchant_risk_category
        
    FROM stg_merchant
)

SELECT
    -- add columns comma separated
    merchant_id,
    merchant_name,
    merchant_category,
    merchant_risk_score,
    ingestion_date,
    -- flags
    is_high_risk_merchant,
    -- Derived risk classification
    merchant_risk_category
FROM 
    infer_columns
