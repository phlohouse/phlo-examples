"""PokeAPI DLT helper."""

from dlt.sources.rest_api import rest_api_source


def pokeapi(resource: str, limit: int = 100):
    """Create a DLT source for PokeAPI resource."""
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
