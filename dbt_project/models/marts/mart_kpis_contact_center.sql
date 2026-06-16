-- KPIs operativos del contact center por semana.
-- Grain: una fila por semana.
SELECT
    DATE_TRUNC(contact_date, WEEK(MONDAY))                                          AS week_start,
    COUNT(*)                                                                         AS n_contacts_total,
    COUNTIF(is_abandoned)                                                            AS n_abandoned,
    ROUND(SAFE_DIVIDE(COUNTIF(is_abandoned), COUNT(*)), 4)                          AS abandon_rate,
    ROUND(AVG(CASE WHEN NOT is_abandoned THEN aht_seconds END), 1)                  AS avg_aht_seconds,
    ROUND(
        SAFE_DIVIDE(
            COUNTIF(NOT is_abandoned AND fcr),
            COUNTIF(NOT is_abandoned)
        ), 4
    )                                                                                AS fcr_rate,
    ROUND(AVG(CASE WHEN NOT is_abandoned THEN csat_score END), 2)                   AS avg_csat
FROM {{ ref('fct_contacts') }}
GROUP BY week_start
ORDER BY week_start
