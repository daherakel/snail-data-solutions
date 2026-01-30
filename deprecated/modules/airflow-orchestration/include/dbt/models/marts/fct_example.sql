{{
    config(
        materialized='table',
        tags=['marts', 'example']
    )
}}

-- Modelo de ejemplo que usa el staging
-- Este se materializa como tabla

with staging as (

    select * from {{ ref('stg_example') }}

)

select
    id,
    upper(name) as name_upper,
    created_at,
    current_timestamp as processed_at
from staging
