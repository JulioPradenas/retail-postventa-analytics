-- Distribución de contactos por motivo, ordenada por volumen.
-- Grain: una fila por motivo de contacto.
SELECT
    contact_motivo,
    COUNT(*)                                                AS n_contacts,
    COUNT(DISTINCT order_id)                                AS n_orders_afectadas,
    ROUND(
        SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER ()), 4
    )                                                       AS pct_of_contacts
FROM {{ ref('fct_contacts') }}
GROUP BY contact_motivo
ORDER BY n_contacts DESC
