{{
    config(
        materialized='table',
        schema='gold'
    )
}}

WITH cards AS (
    SELECT * FROM {{ source('dagster_assets', 'pokemon_cards') }}
),

pokemon AS (
    SELECT * FROM {{ ref('dim_pokemon') }}
),

joined AS (
    SELECT
        c.card_name,
        c.set_name,
        c.set_number,
        c.price_gbp,
        p.pokemon_id,
        p.region,
        p.generation
    FROM cards c
    LEFT JOIN pokemon p
        ON LOWER(TRIM(SPLIT_PART(c.card_name, ' ', 1))) = p.pokemon_name
)

SELECT * FROM joined
ORDER BY price_gbp DESC
