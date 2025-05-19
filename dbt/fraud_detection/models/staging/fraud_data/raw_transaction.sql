WITH base AS (
    SELECT *
    FROM {{ source('fraud_data', 'transactions') }}
)

SELECT * FROM base