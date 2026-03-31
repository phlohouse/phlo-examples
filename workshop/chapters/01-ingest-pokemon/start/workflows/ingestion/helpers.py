"""PokeAPI DLT helper."""

from dlt.sources.rest_api import rest_api_source


def pokeapi(resource: str, limit: int = 100):
    """Create a DLT source for a PokeAPI resource.

    Args:
        resource: API resource name (pokemon, type, ability, move, generation)
        limit: Number of items to fetch

    Returns:
        DLT REST API source
    """
    # TODO: Configure the REST API source
    # Hints:
    #   - base_url is "https://pokeapi.co/api/v2/"
    #   - resource name is both the endpoint path and the resource name
    #   - use "results" as the data_selector (PokeAPI wraps data in a results array)
    #   - pass limit and offset=0 as params
    pass
