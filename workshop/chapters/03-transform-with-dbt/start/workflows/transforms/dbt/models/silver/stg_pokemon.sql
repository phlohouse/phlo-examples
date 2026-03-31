{{
    config(
        materialized='table',
        schema='silver'
    )
}}

-- TODO: Stage Pokemon data
-- 1. Select from {{ source('dagster_assets', 'pokemon') }}
-- 2. Extract pokemon_id from URL using REGEXP_EXTRACT(url, '/pokemon/(\d+)/', 1)
-- 3. Cast pokemon_id to INTEGER
-- 4. Clean name with LOWER(TRIM(name))
-- 5. Keep url as api_url
-- 6. Keep _phlo_ingested_at and _phlo_partition_date
-- 7. Filter WHERE name IS NOT NULL
