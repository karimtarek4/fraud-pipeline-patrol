-- Configure S3 directly in the model for testing
{{ config(
    materialized = 'table'
) }}

WITH connection_test AS (
    SELECT *
    FROM {{ source('fraud_detection', 'customers') }}
)

SELECT * FROM connection_test LIMIT 10