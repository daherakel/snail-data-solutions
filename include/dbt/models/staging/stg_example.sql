{{
    config(
        materialized='view',
        tags=['staging', 'example']
    )
}}

-- Este es un modelo de ejemplo
-- Reemplazar con tus propias tablas y lógica

with source_data as (

    select
        1 as id,
        'Example Data' as name,
        current_timestamp as created_at

)

select
    id,
    name,
    created_at
from source_data
