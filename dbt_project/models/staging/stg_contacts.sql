WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_contacts') }}
)

SELECT
    contact_id,
    order_id,
    CAST(contact_date AS DATE)          AS contact_date,
    contact_channel,
    contact_motivo,
    CAST(is_abandoned AS BOOL)          AS is_abandoned,
    agent_id,
    CAST(aht_seconds AS INT64)          AS aht_seconds,
    CAST(csat_score AS INT64)           AS csat_score,
    CAST(fcr AS BOOL)                   AS fcr
FROM source
