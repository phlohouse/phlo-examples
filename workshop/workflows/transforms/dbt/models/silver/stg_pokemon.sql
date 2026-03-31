{{
    config(
        materialized='table',
        schema='silver'
    )
}}

/*
  Staged Pokemon data
  - Extracts Pokemon ID from URL
  - Cleans names
*/

WITH source AS (
    SELECT * FROM {{ source('dagster_assets', 'pokemon') }}
),

staged AS (
    SELECT
        CAST(
            REGEXP_EXTRACT(url, '/pokemon/(\d+)/', 1) AS INTEGER
        ) AS pokemon_id,
        LOWER(TRIM(name)) AS pokemon_name,
        url AS api_url,
        _phlo_ingested_at,
        _phlo_partition_date
    FROM source
    WHERE name IS NOT NULL
)

SELECT * FROM staged
