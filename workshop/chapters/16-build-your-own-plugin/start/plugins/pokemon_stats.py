"""Pokemon stats CLI plugin."""

import click

from phlo.plugins import PluginMetadata
from phlo.plugins.base.cli import CliCommandPlugin


class PokemonStatsPlugin(CliCommandPlugin):
    """CLI plugin that prints Pokemon statistics from Trino."""

    @property
    def metadata(self) -> PluginMetadata:
        # TODO: Return PluginMetadata with:
        #   - name: "pokemon-stats"
        #   - version: "0.1.0"
        #   - description: "Pokemon statistics CLI command"
        pass

    def get_cli_commands(self) -> list[click.Command]:
        # TODO: Return a list containing the pokemon_group command
        pass


# TODO: Create a Click group called "pokemon" with a "stats" subcommand
# The stats command should:
# 1. Query Trino for total Pokemon count (SELECT COUNT(*) FROM raw.pokemon)
# 2. Query Trino for type count (SELECT COUNT(*) FROM raw.pokemon_types)
# 3. Print formatted output
