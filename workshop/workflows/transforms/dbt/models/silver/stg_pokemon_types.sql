{{
    config(
        materialized='table',
        schema='silver'
    )
}}

/*
  Staged Pokemon types
  - Extracts type ID from URL
  - Cleans names
*/

WITH source AS (
    SELECT * FROM {{ source('dagster_assets', 'pokemon_types') }}
),

staged AS (
    SELECT
        CAST(
            REGEXP_EXTRACT(url, '/type/(\d+)/', 1) AS INTEGER
        ) AS type_id,
        LOWER(TRIM(name)) AS type_name,
        url AS api_url,
        _phlo_ingested_at
    FROM source
    WHERE name IS NOT NULL
)

SELECT * FROM staged
