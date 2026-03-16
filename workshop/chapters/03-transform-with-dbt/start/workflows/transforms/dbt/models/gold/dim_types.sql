{{
    config(
        materialized='table',
        schema='gold'
    )
}}

-- TODO: Build Types dimension table
-- 1. Select from {{ ref('stg_pokemon_types') }}
-- 2. Keep type_id and type_name
-- 3. Add type_display_name: capitalize first letter
--    Hint: upper(substr(type_name, 1, 1)) || substr(type_name, 2)
-- 4. Keep api_url and _phlo_ingested_at AS loaded_at
-- 5. ORDER BY type_id
