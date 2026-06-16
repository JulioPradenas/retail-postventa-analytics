-- Devoluciones por motivo con contexto de atraso (devoluciones prevenibles).
-- Grain: una fila por motivo de devolución.
WITH returns_ctx AS (
    SELECT
        r.return_id,
        r.return_motivo,
        r.return_status,
        o.is_late
    FROM {{ ref('stg_returns') }} AS r
    LEFT JOIN {{ ref('fct_orders') }} AS o ON r.order_id = o.order_id
)

SELECT
    return_motivo,
    COUNT(*)                                                        AS n_returns,
    ROUND(SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER ()), 4)         AS pct_of_returns,
    COUNTIF(is_late)                                                AS n_late_related,
    ROUND(SAFE_DIVIDE(COUNTIF(is_late), COUNT(*)), 4)               AS pct_late_related
FROM returns_ctx
GROUP BY return_motivo
ORDER BY n_returns DESC
