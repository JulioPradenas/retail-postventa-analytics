WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_returns') }}
)

SELECT
    return_id,
    order_id,
    CAST(return_date AS DATE)   AS return_date,
    return_motivo,
    return_status
FROM source
