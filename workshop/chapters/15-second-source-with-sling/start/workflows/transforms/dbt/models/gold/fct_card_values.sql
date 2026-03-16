{{
    config(
        materialized='table',
        schema='gold'
    )
}}

-- TODO: Join pokemon cards with pokemon dimension
-- 1. Select from raw.pokemon_cards (use {{ source('dagster_assets', 'pokemon_cards') }})
-- 2. Join with {{ ref('dim_pokemon') }} on card_name matching pokemon_name
-- 3. Select: card_name, set_name, set_number, price_gbp, pokemon_id, region, generation
-- 4. Order by price_gbp DESC
