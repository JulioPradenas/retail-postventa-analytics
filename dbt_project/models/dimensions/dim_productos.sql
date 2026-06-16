WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
)

SELECT DISTINCT
    product_sku,
    product_name,
    product_category,
    product_subcategory,
    unit_price
FROM orders
