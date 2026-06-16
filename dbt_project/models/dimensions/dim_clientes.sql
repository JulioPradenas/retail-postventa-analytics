-- Un registro por cliente con su segmento más reciente.
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

ranked AS (
    SELECT
        customer_id,
        customer_segment,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY order_date DESC
        ) AS rn
    FROM orders
)

SELECT
    customer_id,
    customer_segment
FROM ranked
WHERE rn = 1
