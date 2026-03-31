"""Pokemon ingestion assets."""

from phlo_dlt import phlo_ingestion
from workflows.ingestion.helpers import pokeapi

# TODO: Import your schemas from workflows.schemas.pokemon


# TODO: Create a pokemon ingestion asset
# Use the @phlo_ingestion decorator with:
#   - table_name: "pokemon"
#   - unique_key: "name"
#   - validation_schema: RawPokemon
#   - group: "pokemon"
#   - cron: "0 0 * * 0" (weekly)
#   - freshness_hours: (168, 336)
#   - merge_strategy: "merge"
#
# The function should accept partition_date: str and return pokeapi("pokemon", limit=1025)


# TODO: Create a pokemon_types ingestion asset
# Use the @phlo_ingestion decorator with:
#   - table_name: "pokemon_types"
#   - unique_key: "name"
#   - validation_schema: RawPokemonTypes
#   - group: "pokemon"
#   - cron: "0 0 1 * *" (monthly)
#   - freshness_hours: (720, 1440)
#   - merge_strategy: "merge"
#
# The function should accept partition_date: str and return pokeapi("type", limit=20)
