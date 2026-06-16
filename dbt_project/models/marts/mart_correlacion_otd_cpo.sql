-- ⭐ Insight estrella: OTD y CPO por semana, alineados a nivel de orden.
-- Une cada orden con su contacto (si existe) para evitar desfase de fechas.
-- Expectativa: órdenes atrasadas → tasa de contacto ~67% vs ~29% en tiempo.
-- Grain: una fila por semana (por order_date).
WITH order_contacts AS (
    SELECT
        o.order_id,
        o.order_date,
        o.is_late,
        IF(c.order_id IS NOT NULL, 1, 0) AS has_contact
    FROM {{ ref('fct_orders') }} AS o
    LEFT JOIN (
        SELECT DISTINCT order_id
        FROM {{ ref('fct_contacts') }}
    ) AS c ON o.order_id = c.order_id
),

weekly AS (
    SELECT
        DATE_TRUNC(order_date, WEEK(MONDAY))                            AS week_start,
        COUNT(*)                                                         AS n_orders,
        COUNTIF(is_late)                                                 AS n_late,
        SUM(has_contact)                                                 AS n_contacts,
        ROUND(SAFE_DIVIDE(COUNTIF(NOT is_late), COUNT(*)), 4)           AS otd_rate,
        ROUND(SAFE_DIVIDE(SUM(has_contact), COUNT(*)), 4)               AS cpo
    FROM order_contacts
    GROUP BY 1
)

SELECT
    week_start,
    n_orders,
    n_late,
    n_contacts,
    otd_rate,
    cpo,
    CASE
        WHEN otd_rate >= 0.90 THEN 'OTD >= 90%'
        WHEN otd_rate >= 0.80 THEN 'OTD 80-90%'
        ELSE                       'OTD < 80%'
    END AS otd_bucket
FROM weekly
ORDER BY week_start
