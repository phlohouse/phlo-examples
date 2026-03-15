"""Pokemon stats CLI plugin."""

from __future__ import annotations

import subprocess
import sys

import click

from phlo.plugins import PluginMetadata
from phlo.plugins.base.cli import CliCommandPlugin


class PokemonStatsPlugin(CliCommandPlugin):
    """CLI plugin that prints Pokemon statistics from Trino."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="pokemon-stats",
            version="0.1.0",
            description="Pokemon statistics CLI command",
        )

    def get_cli_commands(self) -> list[click.Command]:
        return [pokemon_group]


def _query_trino(sql: str) -> str:
    """Run a SQL query against Trino via the Phlo CLI."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "phlo.cli.main",
            "trino",
            "query",
            sql,
            "--catalog",
            "iceberg",
            "--schema",
            "raw",
            "--output-format",
            "CSV",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise click.ClickException(f"Trino query failed: {result.stderr.strip()}")
    return result.stdout.strip()


@click.group(name="pokemon")
def pokemon_group():
    """Pokemon data commands."""
    pass


@pokemon_group.command()
def stats():
    """Print Pokemon statistics from the lakehouse."""
    click.echo("Pokemon Statistics")
    click.echo("=" * 40)

    # Total Pokemon
    count = int(_query_trino("SELECT COUNT(*) FROM pokemon").strip('"'))
    click.echo(f"  Total Pokemon:  {count}")

    # Total types
    types = int(_query_trino("SELECT COUNT(*) FROM pokemon_types").strip('"'))
    click.echo(f"  Total Types:    {types}")

    # Per-generation breakdown (if gold tables exist)
    try:
        output = _query_trino(
            "SELECT generation, COUNT(*) as cnt "
            "FROM gold.dim_pokemon GROUP BY generation ORDER BY generation"
        )
        click.echo("\n  By Generation:")
        for line in output.strip().split("\n"):
            if line.strip():
                parts = line.strip().strip('"').split('","')
                if len(parts) == 2:
                    gen, cnt = parts
                    click.echo(f"    Gen {gen}: {cnt}")
    except Exception:
        click.echo("\n  (Run Chapter 03 for per-generation stats)")

    click.echo()
