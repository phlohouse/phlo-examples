"""Helper functions for PokeAPI ingestion.

This is project-specific code to reduce repetition across Pokemon workflows.
"""

from __future__ import annotations

from typing import Any

from dlt.sources.rest_api import rest_api_source


def pokeapi(resource: str, limit: int = 100) -> Any:
    """
    Helper to create DLT sources for PokeAPI endpoints.

    Reduces repetition across Pokemon ingestion workflows in this project.

    Args:
        resource: API resource name (pokemon, type, ability, move, generation)
        limit: Number of items to fetch

    Returns:
        DLT rest_api_source
    """
    config = {
        "client": {
            "base_url": "https://pokeapi.co/api/v2/",
        },
        "resources": [
            {
                "name": resource,
                "endpoint": {
                    "path": resource,
                    "params": {"limit": limit, "offset": 0},
                    "data_selector": "results",
                },
            },
        ],
    }
    return rest_api_source(config)
