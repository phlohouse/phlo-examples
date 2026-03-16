{{
    config(
        materialized='table',
        schema='silver'
    )
}}

-- TODO: Stage Pokemon types data
-- 1. Select from {{ source('dagster_assets', 'pokemon_types') }}
-- 2. Extract type_id from URL using REGEXP_EXTRACT(url, '/type/(\d+)/', 1)
-- 3. Cast type_id to INTEGER
-- 4. Clean name with LOWER(TRIM(name))
-- 5. Keep url as api_url
-- 6. Keep _phlo_ingested_at
-- 7. Filter WHERE name IS NOT NULL
