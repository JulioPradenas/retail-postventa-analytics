-- Cumplimiento de promesa de entrega (OTD) por carrier y zona.
-- Grain: una fila por carrier × zona.
SELECT
    carrier,
    carrier_modality,
    zone,
    COUNT(*)                                                    AS n_shipments,
    COUNTIF(NOT is_late)                                        AS n_on_time,
    COUNTIF(is_late)                                            AS n_late,
    ROUND(SAFE_DIVIDE(COUNTIF(NOT is_late), COUNT(*)), 4)       AS otd_rate,
    ROUND(AVG(CASE WHEN is_late THEN delay_days END), 2)        AS avg_delay_days_when_late
FROM {{ ref('fct_orders') }}
GROUP BY carrier, carrier_modality, zone
ORDER BY otd_rate ASC
