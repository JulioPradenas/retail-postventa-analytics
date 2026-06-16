-- En los datos sintéticos cada carrier tiene exactamente una modalidad.
WITH shipments AS (
    SELECT * FROM {{ ref('stg_shipments') }}
)

SELECT DISTINCT
    carrier,
    carrier_modality
FROM shipments
