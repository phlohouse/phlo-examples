{{
    config(
        materialized='table',
        schema='gold'
    )
}}

/*
  Pokemon dimension table
  - Core Pokemon reference data
  - Generation derived from ID ranges
*/

WITH pokemon AS (
    SELECT * FROM {{ ref('stg_pokemon') }}
),

enriched AS (
    SELECT
        pokemon_id,
        pokemon_name,
        -- Derive generation from Pokemon ID ranges
        CASE
            WHEN pokemon_id <= 151 THEN 1
            WHEN pokemon_id <= 251 THEN 2
            WHEN pokemon_id <= 386 THEN 3
            WHEN pokemon_id <= 493 THEN 4
            WHEN pokemon_id <= 649 THEN 5
            WHEN pokemon_id <= 721 THEN 6
            WHEN pokemon_id <= 809 THEN 7
            WHEN pokemon_id <= 905 THEN 8
            ELSE 9
        END AS generation,
        -- Categorize by ID
        CASE
            WHEN pokemon_id <= 151 THEN 'Kanto'
            WHEN pokemon_id <= 251 THEN 'Johto'
            WHEN pokemon_id <= 386 THEN 'Hoenn'
            WHEN pokemon_id <= 493 THEN 'Sinnoh'
            WHEN pokemon_id <= 649 THEN 'Unova'
            WHEN pokemon_id <= 721 THEN 'Kalos'
            WHEN pokemon_id <= 809 THEN 'Alola'
            WHEN pokemon_id <= 905 THEN 'Galar'
            ELSE 'Paldea'
        END AS region,
        api_url,
        _phlo_ingested_at AS loaded_at
    FROM pokemon
)

SELECT * FROM enriched
ORDER BY pokemon_id
