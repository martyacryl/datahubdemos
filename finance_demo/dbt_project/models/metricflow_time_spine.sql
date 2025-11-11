-- Time Spine Model for dbt Semantic Layer
-- This model generates a series of dates that the semantic layer uses for time-based metrics
-- The semantic layer requires this model with granularity DAY or smaller

{{ config(
    materialized='table',
    schema='metrics'
) }}

-- Generate dates from 2020-01-01 to 2030-12-31 (10 years)
-- Adjust the date range as needed for your use case
with date_spine as (
    {{ dbt.date_spine(
        datepart="day",
        start_date="cast('2020-01-01' as date)",
        end_date="cast('2030-12-31' as date)"
    ) }}
)

select 
    date_day as metric_time
from date_spine

