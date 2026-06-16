WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_orders') }}
)

SELECT
    order_id,
    customer_id,
    customer_segment,
    region,
    city,
    CAST(order_date AS DATE)           AS order_date,
    product_sku,
    product_name,
    product_category,
    product_subcategory,
    CAST(quantity AS INT64)            AS quantity,
    CAST(unit_price AS FLOAT64)        AS unit_price,
    CAST(total_amount AS FLOAT64)      AS total_amount
FROM source
