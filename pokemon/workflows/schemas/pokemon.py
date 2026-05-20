"""Pokemon Pandera schemas.

Schemas define data validation rules and auto-generate Iceberg schemas.
"""

from pandera.pandas import Field
from phlo_pandera.schemas import PhloSchema


class RawPokemon(PhloSchema):
    """Raw Pokemon data from PokeAPI.

    Note: PokeAPI /pokemon endpoint returns name + url only.
    The id is extracted from the url path by DLT.
    """

    name: str = Field(description="Pokemon name")
    url: str = Field(description="API URL for full details")


class RawPokemonTypes(PhloSchema):
    """Pokemon types from PokeAPI."""

    name: str = Field(description="Type name (fire, water, grass, etc.)")
    url: str


class RawPokemonAbilities(PhloSchema):
    """Pokemon abilities from PokeAPI."""

    name: str = Field(description="Ability name")
    url: str


class RawPokemonMoves(PhloSchema):
    """Pokemon moves from PokeAPI."""

    name: str = Field(description="Move name")
    url: str


class RawPokemonGenerations(PhloSchema):
    """Pokemon generations from PokeAPI."""

    name: str = Field(description="Generation name (generation-i, etc.)")
    url: str
