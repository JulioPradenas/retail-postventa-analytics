-- Tabla de hechos central: une cada orden con su despacho.
-- Grain: una fila por orden (= un despacho).
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

shipments AS (
    SELECT * FROM {{ ref('stg_shipments') }}
)

SELECT
    -- Claves
    orders.order_id,
    orders.customer_id,
    shipments.shipment_id,
    orders.product_sku,
    shipments.carrier,

    -- Atributos de la orden
    orders.customer_segment,
    orders.region,
    orders.city,
    orders.order_date,
    orders.product_category,
    orders.product_subcategory,
    orders.quantity,
    orders.unit_price,
    orders.total_amount,

    -- Atributos del despacho
    shipments.carrier_modality,
    shipments.zone,
    shipments.promised_delivery_days,
    shipments.promised_date,
    shipments.actual_delivery_date,
    shipments.is_late,
    shipments.delay_days,
    shipments.delivery_status,

    -- Métrica derivada
    DATE_DIFF(shipments.actual_delivery_date, orders.order_date, DAY) AS days_to_delivery

FROM orders
INNER JOIN shipments ON orders.order_id = shipments.order_id
