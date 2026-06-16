-- Tabla de hechos de contactos postventa con contexto de orden y envío.
-- Grain: una fila por contacto.
WITH contacts AS (
    SELECT * FROM {{ ref('stg_contacts') }}
),

orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

shipments AS (
    SELECT * FROM {{ ref('stg_shipments') }}
)

SELECT
    -- Claves
    contacts.contact_id,
    contacts.order_id,
    orders.customer_id,

    -- Atributos del contacto
    contacts.contact_date,
    contacts.contact_channel,
    contacts.contact_motivo,
    contacts.is_abandoned,
    contacts.agent_id,
    contacts.aht_seconds,
    contacts.csat_score,
    contacts.fcr,

    -- Contexto de la orden
    orders.customer_segment,
    orders.region,
    orders.order_date,
    orders.product_category,
    orders.total_amount,

    -- Contexto del envío
    shipments.carrier,
    shipments.is_late,
    shipments.delay_days,
    shipments.actual_delivery_date,

    -- Métricas derivadas
    DATE_DIFF(contacts.contact_date, shipments.actual_delivery_date, DAY) AS days_contact_after_delivery

FROM contacts
LEFT JOIN orders    ON contacts.order_id = orders.order_id
LEFT JOIN shipments ON contacts.order_id = shipments.order_id
