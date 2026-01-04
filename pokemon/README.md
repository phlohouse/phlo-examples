# Phlo Pokemon Demo

A demo project showing how to build a Pokemon data lakehouse with Phlo.
Ingests Pokemon data from PokeAPI into an Iceberg lakehouse.

## Quick Start

### Standard Mode

```bash
cd phlo-examples/pokemon
phlo services init
phlo services start
```

### Development Mode

For developing phlo itself with instant iteration:

```bash
cd phlo-examples/pokemon
phlo services init --dev --phlo-source /path/to/phlo
phlo services start
```

This mounts the phlo monorepo into the Dagster container and installs `phlo[defaults]` as an editable install.

## Services

After starting, access:

- **Dagster UI**: http://localhost:3000 - Orchestration & monitoring
- **Trino**: http://localhost:8080 - Query engine
- **MinIO Console**: http://localhost:9101 - Object storage (minio/minio123)
- **Superset**: http://localhost:8088 - BI dashboards (admin/admin)
- **pgweb**: http://localhost:8081 - Database admin

## Project Structure

```
pokemon/
├── .phlo/                      # Infrastructure config
│   └── dagster/                # Dagster workspace
├── workflows/                  # Data workflows
│   ├── ingestion/              # Ingestion assets (@phlo_ingestion)
│   │   └── pokemon/
│   │       ├── helpers.py      # DLT helper for PokeAPI
│   │       └── pokemon.py      # Pokemon ingestion workflows
│   ├── schemas/                # Pandera validation schemas
│   │   └── pokemon.py          # Pokemon data schemas
│   └── transforms/dbt/         # dbt transformation models (optional)
├── tests/                      # Workflow tests
├── phlo.yaml                   # Infrastructure configuration
└── pyproject.toml              # Project dependencies
```

## DLT Helper Pattern

This project demonstrates the **dedicated helper pattern** for reducing API boilerplate.

### Why Use Helpers?

When you have multiple workflows ingesting from the same API, use a dedicated helper module to:

- Avoid repeating base URL, authentication, and pagination logic
- Ensure consistency across all Pokemon workflows
- Make it easy to update API configuration in one place
- Improve code readability and maintainability

### Implementation

**Helper module** (`workflows/ingestion/pokemon/helpers.py`):

```python
from dlt.sources.rest_api import rest_api_source

def pokeapi(resource: str, limit: int = 100):
    """Helper to create DLT sources for PokeAPI endpoints."""
    config = {
        "client": {
            "base_url": "https://pokeapi.co/api/v2/",
        },
        "resources": [{
            "name": resource,
            "endpoint": {
                "path": resource,
                "params": {"limit": limit, "offset": 0},
                "data_selector": "results",
            },
        }],
    }
    return rest_api_source(config)
```

**Usage in workflows** (`workflows/ingestion/pokemon/pokemon.py`):

```python
from phlo_dlt import phlo_ingestion
from workflows.ingestion.pokemon.helpers import pokeapi
from workflows.schemas.pokemon import RawPokemon

@phlo_ingestion(
    table_name="pokemon",
    unique_key="name",
    validation_schema=RawPokemon,
    group="pokemon",
)
def pokemon(partition_date: str):
    return pokeapi("pokemon", limit=1025)
```

### Benefits

- **Single source of truth**: API configuration lives in one place
- **Consistency**: All workflows use the same pagination and data selection logic
- **Maintainability**: Updating the API client is a one-line change
- **Self-documenting**: Helper function signature shows what parameters are available

### When to Use This Pattern

Use dedicated helpers when you have:

- Multiple workflows for the same API (this project has 5: pokemon, types, abilities, moves, generations)
- Shared authentication or headers
- Common pagination logic
- Consistent query parameters

See the [Developer Guide](../../phlo/docs/guides/developer-guide.md#dlt-helper-pattern-recommended) for complete documentation on this pattern.

## Data Flow

1. **Ingestion**: Five Pokemon data sources
   - `pokemon`: Pokemon list (~1000 Pokemon)
   - `pokemon_types`: Type classifications (fire, water, etc.)
   - `pokemon_abilities`: Pokemon abilities
   - `pokemon_moves`: Pokemon moves
   - `pokemon_generations`: Game generations

2. **Bronze**: Raw data validation and staging

3. **Silver**: Cleaned and enriched data (optional dbt models)

4. **Gold**: Aggregated metrics and analytics (optional dbt models)

## CLI Commands

### Core Operations

```bash
phlo services start          # Start infrastructure
phlo services stop           # Stop infrastructure
phlo services status         # Check health
phlo materialize <asset>     # Materialize asset
phlo test                    # Run test suite
```

### Asset Materialization

```bash
# Single asset
phlo materialize pokemon --partition 2024-01-15

# Multiple assets
phlo materialize pokemon pokemon_types pokemon_abilities

# All Pokemon assets
phlo materialize --select "group:pokemon"

# Via Dagster UI
# Navigate to Assets > select asset > Materialize
```

## Merge Strategy

This project uses the **merge strategy** for all Pokemon data:

```python
@phlo_ingestion(
    table_name="pokemon",
    unique_key="name",
    merge_strategy="merge",  # Upsert mode
    ...
)
```

### Why Merge?

Pokemon data is relatively static but can change:

- New Pokemon are added with new game releases
- Pokemon stats may be rebalanced
- Move lists may be updated
- Running the pipeline multiple times should update existing records, not duplicate them

### Alternative: Append Strategy

For truly immutable data sources (like event logs), you would use:

```python
merge_strategy="append"  # Insert-only, no deduplication
```

But for reference data like Pokemon, merge is the right choice.

## Documentation

- [Phlo Documentation](https://github.com/iamgp/phlo)
- [Developer Guide](../../phlo/docs/guides/developer-guide.md) - DLT helper patterns
- [CLI Reference](../../phlo/docs/reference/cli-reference.md) - All CLI commands

## Learning Path

1. **Start here**: Understand the dedicated helper pattern
2. **Read the code**: See how `helpers.py` reduces boilerplate
3. **Compare with other examples**: GitHub and Nightscout use the same pattern
4. **Build your own**: Apply this pattern to your API sources

## Next Steps

- **Add dbt transformations**: Build silver/gold models
- **Create dashboards**: Connect Superset to Pokemon data
- **Extend with more endpoints**: Add items, berries, locations
