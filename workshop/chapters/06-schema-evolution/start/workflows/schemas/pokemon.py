"""Pokemon Pandera schemas — evolving the schema."""

from pandera.pandas import Field
from phlo_pandera.schemas import PhloSchema


class RawPokemon(PhloSchema):
    """Raw Pokemon data from PokeAPI."""

    name: str = Field(description="Pokemon name")
    url: str = Field(description="API URL for full details")
    # TODO: Add a habitat field
    # - Type: str
    # - nullable=True (not all Pokemon have a habitat)
    # - description="Pokemon habitat"


class RawPokemonTypes(PhloSchema):
    """Pokemon types from PokeAPI."""

    name: str = Field(description="Type name (fire, water, grass, etc.)")
    url: str = Field(description="API URL for full details")
