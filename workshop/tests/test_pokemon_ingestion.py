"""Tests for Pokemon ingestion assets."""

from phlo_testing import mock_dlt_source, test_asset_execution


MOCK_POKEMON = [
    {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"},
    {"name": "charmander", "url": "https://pokeapi.co/api/v2/pokemon/4/"},
    {"name": "squirtle", "url": "https://pokeapi.co/api/v2/pokemon/7/"},
]


def test_pokemon_ingestion_produces_records():
    """Test that Pokemon ingestion processes mock data correctly."""
    source = mock_dlt_source(MOCK_POKEMON, resource_name="pokemon")
    result = test_asset_execution(
        asset_name="dlt_pokemon",
        partition="2024-01-01",
        mock_data=MOCK_POKEMON,
    )
    assert result.success, f"Asset execution failed: {result.error}"
    assert len(result.data) == 3


def test_pokemon_ingestion_handles_empty_data():
    """Test that empty data is handled gracefully."""
    result = test_asset_execution(
        asset_name="dlt_pokemon",
        partition="2024-01-01",
        mock_data=[],
    )
    assert result.success
    assert len(result.data) == 0
