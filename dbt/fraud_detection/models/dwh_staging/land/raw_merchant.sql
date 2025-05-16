WITH base AS (
    SELECT *
    FROM {{ source('fraud_data', 'merchants') }}
)

SELECT * FROM base