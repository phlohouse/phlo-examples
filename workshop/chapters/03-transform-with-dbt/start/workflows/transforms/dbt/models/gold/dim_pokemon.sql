{{
    config(
        materialized='table',
        schema='gold'
    )
}}

-- TODO: Build Pokemon dimension table
-- 1. Select from {{ ref('stg_pokemon') }}
-- 2. Add generation column using CASE WHEN on pokemon_id ranges:
--    <= 151 → 1 (Kanto), <= 251 → 2 (Johto), <= 386 → 3 (Hoenn),
--    <= 493 → 4 (Sinnoh), <= 649 → 5 (Unova), <= 721 → 6 (Kalos),
--    <= 809 → 7 (Alola), <= 905 → 8 (Galar), ELSE 9 (Paldea)
-- 3. Add region column with the same ranges
-- 4. Keep api_url and _phlo_ingested_at AS loaded_at
-- 5. ORDER BY pokemon_id
