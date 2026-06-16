-- Alertas diarias: KPIs fuera de umbral con nivel de prioridad y owner.
-- Solo muestra días con al menos una alerta activa.
-- Grain: una fila por fecha × KPI en alerta.
WITH daily_otd AS (
    SELECT
        order_date                                                          AS metric_date,
        COUNT(*)                                                            AS n_orders,
        ROUND(SAFE_DIVIDE(COUNTIF(NOT is_late), COUNT(*)), 4)              AS otd_rate
    FROM {{ ref('fct_orders') }}
    GROUP BY order_date
),

daily_cc AS (
    SELECT
        contact_date                                                        AS metric_date,
        COUNT(*)                                                            AS n_contacts,
        ROUND(SAFE_DIVIDE(COUNTIF(is_abandoned), COUNT(*)), 4)             AS abandon_rate,
        ROUND(AVG(CASE WHEN NOT is_abandoned THEN csat_score END), 2)      AS avg_csat
    FROM {{ ref('fct_contacts') }}
    GROUP BY contact_date
),

combined AS (
    SELECT
        COALESCE(o.metric_date, c.metric_date)  AS metric_date,
        o.n_orders,
        o.otd_rate,
        c.n_contacts,
        c.abandon_rate,
        c.avg_csat
    FROM daily_otd AS o
    FULL OUTER JOIN daily_cc AS c ON o.metric_date = c.metric_date
)

SELECT
    metric_date,
    n_orders,
    otd_rate,
    n_contacts,
    abandon_rate,
    avg_csat,
    -- Nivel de alerta OTD
    CASE
        WHEN otd_rate < 0.80 THEN 'P1'
        WHEN otd_rate < 0.90 THEN 'P2'
    END                                         AS otd_alert,
    -- Nivel de alerta abandono
    CASE
        WHEN abandon_rate > 0.25 THEN 'P1'
        WHEN abandon_rate > 0.20 THEN 'P2'
    END                                         AS abandon_alert,
    -- Nivel de alerta CSAT
    CASE
        WHEN avg_csat < 2.5 THEN 'P1'
        WHEN avg_csat < 3.0 THEN 'P2'
    END                                         AS csat_alert,
    -- Owner por KPI
    CASE
        WHEN otd_rate < 0.80 THEN 'Operaciones'
        WHEN otd_rate < 0.90 THEN 'Logística'
    END                                         AS otd_owner,
    CASE
        WHEN abandon_rate > 0.20 THEN 'Contact Center'
    END                                         AS abandon_owner
FROM combined
WHERE
    otd_rate    < 0.90
    OR abandon_rate > 0.20
    OR avg_csat     < 3.0
ORDER BY metric_date
