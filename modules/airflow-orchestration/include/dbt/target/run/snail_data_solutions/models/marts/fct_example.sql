
  
    

  create  table "postgres"."public_marts"."fct_example__dbt_tmp"
  
  
    as
  
  (
    

-- Modelo de ejemplo que usa el staging
-- Este se materializa como tabla

with staging as (

    select * from "postgres"."public_staging"."stg_example"

)

select
    id,
    upper(name) as name_upper,
    created_at,
    current_timestamp as processed_at
from staging
  );
  