-- CPO (contactos por orden) agregado por semana.
-- Grain: una fila por semana calendario (lunes a domingo).
WITH weekly_orders AS (
    SELECT
        DATE_TRUNC(order_date, WEEK(MONDAY))  AS week_start,
        COUNT(DISTINCT order_id)               AS n_orders
    FROM {{ ref('fct_orders') }}
    GROUP BY 1
),

weekly_contacts AS (
    SELECT
        DATE_TRUNC(contact_date, WEEK(MONDAY)) AS week_start,
        COUNT(DISTINCT contact_id)              AS n_contacts
    FROM {{ ref('fct_contacts') }}
    GROUP BY 1
)

SELECT
    o.week_start,
    o.n_orders,
    COALESCE(c.n_contacts, 0)                                   AS n_contacts,
    ROUND(SAFE_DIVIDE(COALESCE(c.n_contacts, 0), o.n_orders), 4) AS cpo
FROM weekly_orders AS o
LEFT JOIN weekly_contacts AS c ON o.week_start = c.week_start
ORDER BY o.week_start
