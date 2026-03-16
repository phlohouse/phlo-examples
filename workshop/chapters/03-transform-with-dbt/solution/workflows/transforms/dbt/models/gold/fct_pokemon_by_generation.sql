{{
    config(
        materialized='table',
        schema='gold'
    )
}}

/*
  Pokemon summary metrics by generation
  - Aggregated stats for analytics dashboards
*/

WITH pokemon AS (
    SELECT * FROM {{ ref('dim_pokemon') }}
),

by_generation AS (
    SELECT
        generation,
        region,
        COUNT(*) AS pokemon_count,
        MIN(pokemon_id) AS first_pokemon_id,
        MAX(pokemon_id) AS last_pokemon_id
    FROM pokemon
    GROUP BY generation, region
)

SELECT
    generation,
    region,
    pokemon_count,
    first_pokemon_id,
    last_pokemon_id,
    ROUND(100.0 * pokemon_count / SUM(pokemon_count) OVER (), 2) AS pct_of_total
FROM by_generation
ORDER BY generation
