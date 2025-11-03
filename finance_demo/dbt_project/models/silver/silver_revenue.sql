-- Silver Layer: Cleaned and Enriched Revenue Data
-- This model cleans and enriches the raw revenue transaction data
-- It joins with customer information to add customer details

{{ config(
    materialized='view',
    schema='silver',
    meta={
        'data_tier': 'Silver',
        'domain': 'Revenue',
        'financial_classification': 'Financial',
        'is_sensitive': True,
        'has_pii': False
    }
) }}

WITH revenue_transactions AS (
    SELECT
        transaction_id,
        customer_id,
        product_id,
        amount,
        transaction_date,
        region,
        currency,
        created_at
    FROM {{ source('bronze', 'revenue_transactions') }}
    WHERE transaction_date IS NOT NULL
      AND amount > 0
),

customer_info AS (
    SELECT
        customer_id,
        customer_name,
        country,
        customer_segment
    FROM {{ source('bronze', 'customer_info') }}
)

SELECT
    rt.transaction_id,
    rt.customer_id,
    ci.customer_name,
    ci.customer_segment,
    ci.country AS customer_country,
    rt.product_id,
    rt.amount,
    rt.transaction_date,
    rt.region,
    rt.currency,
    -- Add calculated fields
    EXTRACT(YEAR FROM rt.transaction_date) AS transaction_year,
    EXTRACT(QUARTER FROM rt.transaction_date) AS transaction_quarter,
    EXTRACT(MONTH FROM rt.transaction_date) AS transaction_month,
    rt.created_at
FROM revenue_transactions rt
LEFT JOIN customer_info ci
    ON rt.customer_id = ci.customer_id

