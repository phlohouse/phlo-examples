# Chapter 16 — Build Your Own Plugin

The capstone — extend Phlo with a custom CLI command, Observatory page, table format swap, and tests.

## What You'll Learn

- Phlo's plugin system and entry points — how plugins are discovered and loaded.
- Writing CLI command plugins — subclassing `CliCommandPlugin` to add `phlo` subcommands.
- Observatory UI extensions — adding custom pages to the Observatory web app.
- Swapping table formats — moving a table from Iceberg to Delta Lake.
- Testing assets with `phlo-testing` — mock fixtures for ingestion pipelines.

## Prerequisites

All previous chapters complete. Services must be running:

```bash
phlo services start
```

---

This chapter has four exercises. Work through them in order.

---

## Exercise 16a — Custom CLI Plugin

Write a `phlo pokemon stats` CLI command that queries Trino and prints Pokemon statistics.

### Step 1: Create the Plugin File

Create `plugins/pokemon_stats.py`:

```python
"""Pokemon stats CLI plugin."""

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
```

Key points:
- `CliCommandPlugin` is the base class for CLI plugins. You implement `metadata` and `get_cli_commands()`.
- `PluginMetadata` identifies the plugin to the registry.
- `get_cli_commands()` returns Click commands/groups that get mounted under `phlo`.

### Step 2: Add the Click Commands

In the same file, define a Click group with a `stats` subcommand:

```python
def _query_trino(sql: str) -> str:
    """Run a SQL query against Trino via the Phlo CLI."""
    result = subprocess.run(
        [
            sys.executable, "-m", "phlo.cli.main", "trino", "query", sql,
            "--catalog", "iceberg", "--schema", "raw", "--output-format", "CSV",
        ],
        capture_output=True, text=True, timeout=30,
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

    count = int(_query_trino("SELECT COUNT(*) FROM pokemon").strip('"'))
    click.echo(f"  Total Pokemon:  {count}")

    types = int(_query_trino("SELECT COUNT(*) FROM pokemon_types").strip('"'))
    click.echo(f"  Total Types:    {types}")
```

### Step 3: Register the Entry Point

Add to your `pyproject.toml`:

```toml
[project.entry-points."phlo.plugins.cli"]
pokemon-stats = "plugins.pokemon_stats:PokemonStatsPlugin"
```

### Step 4: Install and Run

```bash
uv sync --all-extras
phlo pokemon stats
```

Expected output:

```
Pokemon Statistics
========================================
  Total Pokemon:  1025
  Total Types:    20
```

---

## Exercise 16b — Observatory Extension

Add a "Pokemon Dashboard" page to Observatory following the `phlo-observatory-example` pattern.

### Step 1: Create the Extension Plugin

Create `plugins/pokemon_observatory.py`:

```python
"""Pokemon Observatory extension."""

from phlo_observatory.manifest import ExtensionManifest, NavItem, Route
from phlo_observatory.observatory_ext import ObservatoryExtensionPlugin


class PokemonDashboardPlugin(ObservatoryExtensionPlugin):
    """Adds a Pokemon Dashboard page to Observatory."""

    @property
    def manifest(self) -> ExtensionManifest:
        return ExtensionManifest(
            name="pokemon-dashboard",
            version="0.1.0",
            routes=[
                Route(
                    path="/extensions/pokemon",
                    asset_path="plugins/observatory_assets/pokemon.js",
                ),
            ],
            nav=[
                NavItem(label="Pokemon Dashboard", path="/extensions/pokemon", icon="pokeball"),
            ],
        )
```

### Step 2: Create the Frontend Asset

Create `plugins/observatory_assets/pokemon.js`:

```javascript
// Simple Pokemon type distribution chart
export function render(container) {
  container.innerHTML = `
    <h2>Pokemon Dashboard</h2>
    <p>Type distribution loaded from the lakehouse.</p>
    <div id="pokemon-types"></div>
  `;
}
```

### Step 3: Register the Entry Point

Add to `pyproject.toml`:

```toml
[project.entry-points."phlo.plugins.observatory"]
pokemon-dashboard = "plugins.pokemon_observatory:PokemonDashboardPlugin"
```

---

## Exercise 16c — Swap Table Format

Switch one table from Iceberg to Delta Lake to see pluggable table formats in action.

### Step 1: Install Delta Dependencies

```bash
uv pip install -e ".[delta]"
```

### Step 2: Configure Delta Catalog in Trino

Add a Delta catalog configuration to your Trino setup. This registers a second catalog that reads Delta tables from the same MinIO storage.

### Step 3: Re-materialize with Delta

Update one ingestion asset to use Delta format, then re-materialize:

```bash
phlo materialize --select dlt_pokemon_types --table-format delta
```

### Step 4: Query Both Formats

```bash
phlo trino
```

```sql
-- Original Iceberg table
SELECT COUNT(*) FROM iceberg.raw.pokemon;

-- New Delta table
SELECT COUNT(*) FROM delta.raw.pokemon_types;
```

Both catalogs query the same data — different table formats, same SQL interface.

---

## Exercise 16d — Testing with phlo-testing

Write tests for your ingestion assets using `phlo-testing` mock fixtures.

### Step 1: Install Testing Dependencies

```bash
uv pip install -e ".[testing]"
```

### Step 2: Create the Test File

Create `tests/test_pokemon_ingestion.py`:

```python
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
```

### Step 3: Run Tests

```bash
pytest tests/test_pokemon_ingestion.py
```

---

## Check Your Work

```bash
python chapters/16-build-your-own-plugin/check.py
```

Expected output:

```
Chapter 16 — Build Your Own Plugin

  ✓ plugins/pokemon_stats.py defines PokemonStatsPlugin
  ✓ tests/test_pokemon_ingestion.py has test functions
  ✓ pokemon table: 1025 rows

All checks passed!
```

## What You Built

Across four exercises you:

1. **Extended the CLI** — added `phlo pokemon stats` via the plugin system.
2. **Extended the UI** — added a Pokemon Dashboard page to Observatory.
3. **Swapped table formats** — moved a table from Iceberg to Delta with one flag.
4. **Tested pipelines** — wrote unit tests with mock fixtures from `phlo-testing`.

You've now touched every layer of Phlo: ingestion, quality, transforms, storage, catalog, observability, APIs, UI, plugins, and testing. Go build something.
