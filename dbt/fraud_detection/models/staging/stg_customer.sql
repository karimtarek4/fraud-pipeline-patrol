WITH source AS (
    SELECT * FROM {{ ref('raw_customer') }}
),

cleaned AS (
    SELECT
        -- Identity fields
        CustomerID AS customer_id,
        
        -- Date fields
        AccountCreationDate AS account_creation_date,
        
        -- Demographic information
        Age AS age,
        
        -- Financial metrics
        AvgTransactionAmount AS avg_transaction_amount,
        COALESCE(PastFraudCount, 0) AS past_fraud_count,
        
        -- Device and location info
        TRIM(COALESCE(HomeDevice, 'Unknown')) AS home_device,
        TRIM(HomeIP) AS home_ip,  -- Added missing AS keyword
        HomeLat AS home_latitude,
        HomeLon AS home_longitude,
        
        -- Temporal dimensions
        AccountCreationMonth AS account_creation_month,
        EXTRACT(YEAR FROM AccountCreationDate) AS account_creation_year,
        
        -- System fields
        ingestion_date
    FROM source
),

final AS (
    SELECT
        *,
        -- Derived risk classification based on fraud history
        CASE 
            WHEN past_fraud_count > 5 THEN 'High'
            WHEN past_fraud_count > 2 THEN 'Medium'
            ELSE 'Low'
        END AS risk_level,
        
        -- Flag accounts with concerning patterns
        (past_fraud_count > 0) AS has_fraud_history
    FROM cleaned
)

-- Final output with all cleaned and derived fields
SELECT 
    customer_id,
    account_creation_date,
    age,
    avg_transaction_amount,
    past_fraud_count,
    home_device,
    home_ip, 
    home_latitude,
    home_longitude,
    account_creation_month,
    account_creation_year,
    risk_level,
    has_fraud_history,
    ingestion_date
 FROM final
