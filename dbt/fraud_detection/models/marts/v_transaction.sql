{{ config(
    materialized='external',
    location='s3://fraud-data-processed/marts/v_transaction.parquet',
    format='parquet'
) }}


with final as (
    SELECT
        *,
        -- select all columns from dim_customer using dbtstar
        -- and dim_merchant using dbtstar
        {{ dbt_utils.star(from=ref('dim_customer'), relation_alias='c', except=["customer_id"]) }},
        {{ dbt_utils.star(from=ref('dim_merchant'), relation_alias='m', except=["merchant_id"]) }}
    FROM
        {{ ref('fact_transaction') }} ft
    LEFT JOIN
        {{ ref('dim_customer') }} c ON ft.customer_id = c.customer_id
    LEFT JOIN
        {{ ref('dim_merchant') }} m ON ft.merchant_id = m.merchant_id

)
SELECT
    -- Keys
    transaction_id,
    customer_id,
    merchant_id,

    -- Transaction details from fact table
    transaction_timestamp,
    transaction_amount,
    device_id,
    ip_address,
    channel,
    latitude,
    longitude,
    transaction_time_of_day,
    is_high_value_transaction,

    -- Additional fraud risk indicators
    has_elevated_fraud_risk,

    -- Distance calculation between transaction and customer home location
    distance_from_home,

    -- Customer dimension attributes
    age as customer_age,
    past_fraud_count as customer_past_fraud_count,
    home_ip as customer_home_ip,
    home_latitude as customer_home_latitude,
    home_longitude as customer_home_longitude,
    has_fraud_history as customer_has_fraud_history,
    age_tier as customer_age_tier,
    risk_level as customer_risk_level,

    -- Merchant dimension attributes
    merchant_name as merchant_name,
    merchant_risk_category as merchant_risk_category,
    is_high_risk_merchant as is_high_risk_merchant

FROM
    final
