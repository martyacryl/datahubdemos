{{ config(
    materialized='table',
    schema='metrics'
) }}

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