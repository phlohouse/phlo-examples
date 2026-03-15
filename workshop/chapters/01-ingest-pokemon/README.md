# Chapter 01 — Ingest Pokemon

Your first data pipeline: pull Pokemon data from an API into queryable Iceberg tables.

## What You'll Learn

- How `@phlo_ingestion` works — the decorator that turns a function into a managed ingestion asset.
- How DLT REST API sources connect to the decorator — you write a small helper, the decorator handles everything else.
- How data flows: **PokeAPI → DLT → Iceberg (MinIO) → Trino**.
- **Dagster** as the orchestration layer — how assets appear in the UI, how to trigger runs, and how to read run logs.

## Prerequisites

Services must be running:

```bash
phlo services start
```

---

## Step 1: Create the PokeAPI Helper

DLT's `rest_api_source` is a generic connector for REST APIs. You configure it with a base URL, resource endpoints, and pagination params — DLT handles the HTTP requests and yields records.

Create `workflows/ingestion/helpers.py`:

```python
"""PokeAPI DLT helper."""

from dlt.sources.rest_api import rest_api_source


def pokeapi(resource: str, limit: int = 100):
    """Create a DLT source for a PokeAPI resource."""
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
```

Key points:
- `base_url` — the API root. DLT appends resource paths to this.
- `name` — becomes the DLT resource name (and maps to the table name).
- `data_selector` — PokeAPI wraps results in `{"results": [...]}`. This tells DLT where the actual records are.
- `params` — query string parameters. PokeAPI uses `limit` and `offset` for pagination.

## Step 2: Define the Ingestion Asset

The `@phlo_ingestion` decorator wraps your function into a Dagster asset with built-in DLT loading, Iceberg storage, and freshness monitoring.

Create `workflows/ingestion/pokemon.py`:

```python
"""Pokemon ingestion assets."""

from phlo_dlt import phlo_ingestion
from workflows.ingestion.helpers import pokeapi


@phlo_ingestion(
    table_name="pokemon",
    unique_key="name",
    group="pokemon",
    cron="0 0 * * 0",
    freshness_hours=(168, 336),
    merge_strategy="merge",
)
def pokemon(partition_date: str):
    """Ingest Pokemon list from PokeAPI."""
    return pokeapi("pokemon", limit=1025)


@phlo_ingestion(
    table_name="pokemon_types",
    unique_key="name",
    group="pokemon",
    cron="0 0 1 * *",
    freshness_hours=(720, 1440),
    merge_strategy="merge",
)
def pokemon_types(partition_date: str):
    """Ingest Pokemon types."""
    return pokeapi("type", limit=20)
```

Decorator parameters explained:

| Parameter | Purpose |
|---|---|
| `table_name` | Target Iceberg table in the `raw` schema |
| `unique_key` | Deduplication key for merge operations |
| `group` | Logical grouping in the Dagster UI |
| `cron` | Schedule expression (`0 0 * * 0` = weekly Sunday) |
| `freshness_hours` | `(warn, fail)` thresholds for staleness alerts |
| `merge_strategy` | `"merge"` upserts by `unique_key`; `"append"` adds rows |

> Notice: no `validation_schema` yet — we'll add that in Chapter 02.

## Step 3: Materialize

Run the assets to pull data from PokeAPI:

```bash
phlo materialize --select dlt_pokemon
phlo materialize --select dlt_pokemon_types
```

Each command fetches data from the API, writes Parquet files to MinIO, and registers them as Iceberg tables.

## Step 4: Explore the Dagster UI

Every `@phlo_ingestion` function becomes a **Dagster asset** — a unit of data that Dagster tracks, schedules, and monitors. Open the Dagster webserver:

```bash
open http://localhost:3000
```

### Asset graph

Click **Assets** in the left sidebar. You should see your two assets: `dlt_pokemon` and `dlt_pokemon_types`, grouped under "pokemon" (the `group` parameter you set in the decorator).

Click on `dlt_pokemon` to see its detail page:

| Section | What it shows |
|---|---|
| **Materialization history** | Every time the asset was materialized — timestamps, duration, status |
| **Metadata** | Row count, schema, table location in Iceberg |
| **Freshness** | Current staleness vs. the `freshness_hours` thresholds you configured |
| **Upstream / Downstream** | Dependencies between assets (none yet — we'll add them in Chapter 03) |

### Run details

Click **Runs** in the left sidebar. Find the run from your `phlo materialize` command. Click into it to see:

- **Step timeline** — each step (DLT fetch → Iceberg write) as a bar chart.
- **Logs** — structured log output from the pipeline. Filter by log level to find errors or warnings.
- **Asset materializations** — which assets were created/updated in this run.

### Schedules and sensors

Click **Automation** → **Schedules**. Your `cron` parameter (`0 0 * * 0` for weekly) is registered here. Dagster will materialize the asset automatically on this schedule once the daemon is running.

> **Tip:** Leave the Dagster UI open as you work through the workshop — it's the control plane for everything.

## Step 5: Query in Trino

Connect to Trino and inspect your data:

```bash
phlo trino --catalog iceberg --schema raw
```

```sql
SELECT name, url FROM pokemon LIMIT 10;
```

```sql
SELECT COUNT(*) FROM pokemon;
```

```sql
SELECT name, url FROM pokemon_types LIMIT 10;
```

Type `quit` to exit.

## Step 6: Check Your Work

Run the checkpoint script to verify everything landed correctly:

```bash
python chapters/01-ingest-pokemon/check.py
```

Expected output:

```
Chapter 01 — Ingest Pokemon

  ✓ pokemon: 1025 rows
  ✓ pokemon_types: 20 rows

All checks passed!
```

## What You Built

Here's what happened end-to-end:

1. **DLT** fetched records from `https://pokeapi.co/api/v2/pokemon` and `/type`.
2. `@phlo_ingestion` loaded those records into **Iceberg tables** stored in **MinIO** (S3-compatible object storage).
3. **Trino** can query those tables via the Iceberg catalog — no extra setup needed.
4. **Dagster** tracks and schedules everything — assets, runs, freshness, and dependencies are all visible in the UI at `localhost:3000`.

You wrote ~30 lines of Python. Phlo handled schema inference, storage, cataloging, scheduling, and orchestration.

## Next

→ [Chapter 02 — Validate Your Data](../02-validate-your-data/)
