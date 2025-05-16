WITH base AS (
    SELECT *
    FROM {{ source('fraud_data', 'login_attempts') }}
)

SELECT * FROM base