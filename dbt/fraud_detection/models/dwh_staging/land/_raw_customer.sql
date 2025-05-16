WITH base AS (
    SELECT *
    FROM {{ source('fraud_data', 'customers') }}
)

SELECT * FROM base