{{
    config(
        materialized='table',
        schema='gold'
    )
}}

/*
  Types dimension table
*/

WITH types AS (
    SELECT * FROM {{ ref('stg_pokemon_types') }}
)

SELECT
    type_id,
    type_name,
    upper(substr(type_name, 1, 1)) || substr(type_name, 2) AS type_display_name,
    api_url,
    _phlo_ingested_at AS loaded_at
FROM types
ORDER BY type_id
