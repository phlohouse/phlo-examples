{{
    config(
        materialized='table',
        schema='gold'
    )
}}

-- TODO: Build Pokemon by generation fact table
-- 1. Select from {{ ref('dim_pokemon') }}
-- 2. GROUP BY generation, region
-- 3. Calculate:
--    - COUNT(*) AS pokemon_count
--    - MIN(pokemon_id) AS first_pokemon_id
--    - MAX(pokemon_id) AS last_pokemon_id
-- 4. Add pct_of_total: ROUND(100.0 * pokemon_count / SUM(pokemon_count) OVER (), 2)
-- 5. ORDER BY generation
