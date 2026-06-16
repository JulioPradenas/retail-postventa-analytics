WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_shipments') }}
)

SELECT
    shipment_id,
    order_id,
    CAST(order_date AS DATE)                AS order_date,
    carrier,
    carrier_modality,
    zone,
    CAST(promised_delivery_days AS INT64)   AS promised_delivery_days,
    CAST(promised_date AS DATE)             AS promised_date,
    CAST(actual_delivery_date AS DATE)      AS actual_delivery_date,
    CAST(is_late AS BOOL)                   AS is_late,
    CAST(delay_days AS INT64)               AS delay_days,
    delivery_status
FROM source
