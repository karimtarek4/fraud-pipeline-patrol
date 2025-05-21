
/*
  Customer dimension table that provides a comprehensive view of customers
  including their risk profiles, demographics and behavioral attributes.
*/

WITH stg_customer AS (
    SELECT * FROM {{ ref('stg_customer') }}
),

-- Add any additional customer attributes or aggregated metrics
derived_columns AS (
    SELECT
        *,
        -- flags
        (past_fraud_count > 0) AS has_fraud_history,
        -- dates
        -- Use DuckDB's date_part function for better performance
        date_part('month', account_creation_date) AS account_creation_month,
        date_part('year', account_creation_date) AS account_creation_year,
        -- Use DuckDB'sage function for cleaner date calculations
        date_part('day', age(account_creation_date)) AS account_age_days,
        -- Derived categorical grouping 
        CASE
            WHEN age < 25 THEN 'Under 25'
            WHEN age BETWEEN 25 AND 34 THEN '25-34'
            WHEN age BETWEEN 35 AND 44 THEN '35-44'
            WHEN age BETWEEN 45 AND 54 THEN '45-54'
            WHEN age BETWEEN 55 AND 64 THEN '55-64'
            WHEN age >= 65 THEN '65+'
            ELSE 'Unknown'
        END AS age_tier,
        -- Derived risk classification 
        CASE 
            WHEN past_fraud_count > 5 THEN 'High'
            WHEN past_fraud_count > 2 THEN 'Medium'
            ELSE 'Low'
        END AS risk_level
    FROM stg_customer
)

-- Final selection with surrogate key
SELECT
    -- Generate surrogate key using ROW_NUMBER for integer-based key
    row_number() over (order by customer_id) as customer_sk,
    customer_id,
    account_creation_date,
    age,
    past_fraud_count,
    home_device,
    home_ip, 
    home_latitude,
    home_longitude,
    -- flags
    has_fraud_history,
    -- dates
    account_age_days,
    account_creation_month,
    account_creation_year,
    -- Categorical grouping and assessment
    age_tier,
    -- Derived risk classification based on fraud history
    risk_level
FROM 
    derived_columns
