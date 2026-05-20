"""Pokemon ingestion assets with contracts."""

from phlo_dlt import phlo_ingestion
from workflows.ingestion.helpers import pokeapi
from workflows.schemas.pokemon import RawPokemon, RawPokemonTypes
from contracts.pokemon import pokemon_consumer, pokemon_sla


@phlo_ingestion(
    table_name="pokemon",
    unique_key="name",
    validation_schema=RawPokemon,
    consumers=[pokemon_consumer],
    sla=pokemon_sla,
    group="pokemon",
    cron="0 0 * * 0",
    freshness_hours=(168, 336),
    merge_strategy="merge",
)
def pokemon(partition_date: str):
    """Ingest Pokemon list from PokeAPI."""
    return pokeapi("pokemon", limit=1025)


@phlo_ingestion(
    table_name="pokemon_types",
    unique_key="name",
    validation_schema=RawPokemonTypes,
    group="pokemon",
    cron="0 0 1 * *",
    freshness_hours=(720, 1440),
    merge_strategy="merge",
)
def pokemon_types(partition_date: str):
    """Ingest Pokemon types."""
    return pokeapi("type", limit=20)
