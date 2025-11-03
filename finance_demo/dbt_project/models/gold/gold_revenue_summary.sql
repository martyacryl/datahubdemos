-- Gold Layer: Aggregated Revenue Summary
-- This model creates business-ready aggregated revenue summaries
-- Suitable for executive reporting and dashboards

{{ config(
    materialized='view',
    schema='gold',
    meta={
        'data_tier': 'Gold',
        'domain': 'Revenue',
        'financial_classification': 'Financial',
        'is_sensitive': True,
        'has_pii': False,
        'terms_list': 'Revenue,Product Revenue,Financial Metrics'
    }
) }}

WITH silver_revenue AS (
    SELECT
        transaction_id,
        customer_id,
        customer_segment,
        customer_country,
        product_id,
        amount,
        transaction_date,
        region,
        currency,
        transaction_year,
        transaction_quarter,
        transaction_month
    FROM {{ ref('silver_revenue') }}
)

-- Revenue Summary by Product
SELECT
    'product_revenue' AS metric_type,
    product_id,
    NULL AS region,
    NULL AS customer_segment,
    transaction_year,
    transaction_quarter,
    transaction_month,
    COUNT(DISTINCT transaction_id) AS transaction_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_transaction_amount,
    MIN(amount) AS min_transaction_amount,
    MAX(amount) AS max_transaction_amount,
    CURRENT_TIMESTAMP() AS created_at
FROM silver_revenue
GROUP BY
    product_id,
    transaction_year,
    transaction_quarter,
    transaction_month

UNION ALL

-- Revenue Summary by Region
SELECT
    'region_revenue' AS metric_type,
    NULL AS product_id,
    region,
    NULL AS customer_segment,
    transaction_year,
    transaction_quarter,
    transaction_month,
    COUNT(DISTINCT transaction_id) AS transaction_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_transaction_amount,
    MIN(amount) AS min_transaction_amount,
    MAX(amount) AS max_transaction_amount,
    CURRENT_TIMESTAMP() AS created_at
FROM silver_revenue
GROUP BY
    region,
    transaction_year,
    transaction_quarter,
    transaction_month

UNION ALL

-- Revenue Summary by Customer Segment
SELECT
    'segment_revenue' AS metric_type,
    NULL AS product_id,
    NULL AS region,
    customer_segment,
    transaction_year,
    transaction_quarter,
    transaction_month,
    COUNT(DISTINCT transaction_id) AS transaction_count,
    COUNT(DISTINCT customer_id) AS customer_count,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_transaction_amount,
    MIN(amount) AS min_transaction_amount,
    MAX(amount) AS max_transaction_amount,
    CURRENT_TIMESTAMP() AS created_at
FROM silver_revenue
GROUP BY
    customer_segment,
    transaction_year,
    transaction_quarter,
    transaction_month

