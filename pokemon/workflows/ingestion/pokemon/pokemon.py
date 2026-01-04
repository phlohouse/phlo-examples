"""Pokemon ingestion assets using the DLT ingestion decorator."""

from phlo_dlt import phlo_ingestion

from workflows.ingestion.pokemon.helpers import pokeapi
from workflows.schemas.pokemon import (
    RawPokemon,
    RawPokemonAbilities,
    RawPokemonGenerations,
    RawPokemonMoves,
    RawPokemonTypes,
)


@phlo_ingestion(
    table_name="pokemon",
    unique_key="name",  # Use name as unique key since no id in response
    validation_schema=RawPokemon,
    group="pokemon",
    cron="0 0 * * 0",  # Weekly on Sunday
    freshness_hours=(168, 336),  # 1 week warn, 2 weeks fail
    merge_strategy="merge",
)
def pokemon(partition_date: str):
    """Ingest Pokemon list from PokeAPI (Generation 1-9, ~1000 Pokemon)."""
    return pokeapi("pokemon", limit=1025)


@phlo_ingestion(
    table_name="pokemon_types",
    unique_key="name",
    validation_schema=RawPokemonTypes,
    group="pokemon",
    cron="0 0 1 * *",  # Monthly on 1st
    freshness_hours=(720, 1440),  # 30 days warn, 60 days fail
    merge_strategy="merge",
)
def pokemon_types(partition_date: str):
    """Ingest Pokemon types (fire, water, grass, etc.)."""
    return pokeapi("type", limit=20)


@phlo_ingestion(
    table_name="pokemon_abilities",
    unique_key="name",
    validation_schema=RawPokemonAbilities,
    group="pokemon",
    cron="0 0 1 * *",
    freshness_hours=(720, 1440),
    merge_strategy="merge",
)
def pokemon_abilities(partition_date: str):
    """Ingest Pokemon abilities."""
    return pokeapi("ability", limit=400)


@phlo_ingestion(
    table_name="pokemon_moves",
    unique_key="name",
    validation_schema=RawPokemonMoves,
    group="pokemon",
    cron="0 0 1 * *",
    freshness_hours=(720, 1440),
    merge_strategy="merge",
)
def pokemon_moves(partition_date: str):
    """Ingest Pokemon moves."""
    return pokeapi("move", limit=1000)


@phlo_ingestion(
    table_name="pokemon_generations",
    unique_key="name",
    validation_schema=RawPokemonGenerations,
    group="pokemon",
    cron="0 0 1 * *",
    freshness_hours=(720, 1440),
    merge_strategy="merge",
)
def pokemon_generations(partition_date: str):
    """Ingest Pokemon generations."""
    return pokeapi("generation", limit=10)
