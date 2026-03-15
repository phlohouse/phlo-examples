# Chapter 15 — Second Source with Sling

Ingest a CSV file with Sling and join it with your Pokemon data.

## What You'll Learn

- Sling as an alternative ingestion engine — CSV files instead of REST APIs.
- `@phlo_sling_replication` decorator for file-based sources.
- Multi-source data pipelines — combining DLT and Sling assets.
- Joining data from different ingestion engines in dbt.

## Prerequisites

Chapters 01–03 complete — `pokemon` and `dim_pokemon` tables exist in Trino.

---

## Step 1: Examine the Dataset

Open `data/pokemon_cards.csv` — it contains ~85 rows of Pokemon trading card prices:

| Column | Description |
|---|---|
| `set_name` | Trading card set (e.g. "Base Set") |
| `card_name` | Pokemon name on the card |
| `set_number` | Card number within the set |
| `price_gbp` | Card price in GBP |

```bash
head -5 data/pokemon_cards.csv
```

This is a local file, not a REST API. DLT could handle it, but Sling is purpose-built for file and database replications.

## Step 2: Create the Sling Replication Asset

Create `workflows/ingestion/cards.py`:

```python
"""Pokemon trading card ingestion via Sling."""

from phlo_sling import phlo_sling_replication


@phlo_sling_replication(
    stream_name="data/pokemon_cards.csv",
    table_name="pokemon_cards",
    source_conn="file://",
    target_conn="PHLO_ICEBERG",
    group="pokemon",
    mode="full-refresh",
)
def pokemon_cards(runtime):
    """Ingest Pokemon trading card prices from CSV."""
    return None
```

Decorator parameters explained:

| Parameter | Purpose |
|---|---|
| `stream_name` | Path to the source file |
| `table_name` | Target Iceberg table in the `raw` schema |
| `source_conn` | Sling connection string (`file://` for local files) |
| `target_conn` | Sling destination connection (`PHLO_ICEBERG` for the workshop Iceberg catalog) |
| `group` | Logical grouping in the Dagster UI |
| `mode` | `"full-refresh"` replaces the table each run |

Compare with `@phlo_ingestion` from Chapter 01: Sling handles file-level replication, while DLT handles API extraction and transformation. Both produce Iceberg tables in the same `raw` schema.

## Step 3: Materialize

Run the Sling asset:

```bash
phlo materialize --select sling_pokemon_cards
```

Sling reads the CSV, writes Parquet to MinIO, and registers the Iceberg table.

## Step 4: Verify in Trino

Connect to Trino and check the data:

```bash
phlo trino --catalog iceberg --schema raw
```

```sql
SELECT * FROM pokemon_cards LIMIT 10;
```

```sql
SELECT COUNT(*) FROM pokemon_cards;
```

You should see ~85 rows with `set_name`, `card_name`, `set_number`, and `price_gbp` columns.

Type `quit` to exit.

## Step 5: Register the New Raw Source

Update `workflows/transforms/dbt/models/sources.yml` so dbt can read the Sling-ingested table:

```yaml
version: 2

sources:
  - name: dagster_assets
    database: "{{ target.catalog }}"
    schema: raw
    tables:
      - name: pokemon
        description: Raw Pokemon data from PokeAPI
      - name: pokemon_types
        description: Raw Pokemon types from PokeAPI
      - name: pokemon_cards
        description: Raw Pokemon trading card prices from Sling
```

## Step 6: Join with Pokemon Data

Now build a dbt model that joins card prices with the Pokemon dimension from Chapter 03.

Create `workflows/transforms/dbt/models/gold/fct_card_values.sql`:

```sql
{{
    config(
        materialized='table',
        schema='gold'
    )
}}

WITH cards AS (
    SELECT * FROM {{ source('dagster_assets', 'pokemon_cards') }}
),

pokemon AS (
    SELECT * FROM {{ ref('dim_pokemon') }}
),

joined AS (
    SELECT
        c.card_name,
        c.set_name,
        c.set_number,
        c.price_gbp,
        p.pokemon_id,
        p.region,
        p.generation
    FROM cards c
    LEFT JOIN pokemon p
        ON LOWER(TRIM(SPLIT_PART(c.card_name, ' ', 1))) = p.pokemon_name
)

SELECT * FROM joined
ORDER BY price_gbp DESC
```

This model:
1. Reads the Sling-ingested `pokemon_cards` table via `source()`.
2. Joins with `dim_pokemon` (from DLT ingestion + dbt transform).
3. Produces a gold-layer fact table ordered by card value.

## Step 7: Run dbt

Compile and run the model:

```bash
phlo dbt run --select fct_card_values
```

Then query the result:

```bash
phlo trino --catalog iceberg --schema gold
```

```sql
SELECT card_name, set_name, price_gbp, region, generation
FROM fct_card_values
LIMIT 10;
```

## Step 8: Check Your Work

Run the checkpoint script:

```bash
python chapters/15-second-source-with-sling/check.py
```

Expected output:

```
Chapter 15 — Second Source with Sling

  ✓ raw.pokemon_cards: 85 rows
  ✓ gold.fct_card_values: 1 rows

All checks passed!
```

## What You Built

1. **Sling replication** — ingested a CSV file using `@phlo_sling_replication` instead of DLT.
2. **Multi-source pipeline** — combined data from two different ingestion engines (DLT + Sling) in the same `raw` schema.
3. **Cross-source join** — built a dbt model that joins Sling-ingested card data with DLT-ingested Pokemon data.

Phlo treats all ingestion engines as first-class — DLT for APIs, Sling for files and databases. Both produce Iceberg tables that dbt can transform.

## Next

→ [Chapter 16 — Build Your Own Plugin](../16-build-your-own-plugin/)
