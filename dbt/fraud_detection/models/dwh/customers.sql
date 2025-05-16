WITH customers AS (
    SELECT *
    FROM {{ source('fraud_detection', 'customers') }}
)

SELECT * FROM customers