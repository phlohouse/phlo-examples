# Chapter 06 — Schema Evolution

Evolve your Pandera schemas safely — classify changes, generate migration plans, and apply them without breaking downstream consumers.

## What You'll Learn

- Schema registry — how Phlo tracks schema versions over time.
- Migration plans — previewing and applying structural changes to Iceberg tables.
- Change classification — understanding breaking vs compatible (widening) changes.
- `phlo schema-migrate` CLI — diffing, planning, and applying schema migrations.

## Prerequisites

Chapter 05 complete — `pokemon` table exists in Trino with a validated schema.

---

## Step 1: Add a New Field to the Schema

Edit `workflows/schemas/pokemon.py` and add a `habitat` field to `RawPokemon`:

```python
class RawPokemon(PhloSchema):
    """Raw Pokemon data from PokeAPI."""

    name: str = Field(description="Pokemon name")
    url: str = Field(description="API URL for full details")
    habitat: str = Field(nullable=True, description="Pokemon habitat")
```

Key points:

| Detail | Why it matters |
|---|---|
| `nullable=True` | Makes this a **compatible** (widening) change — existing rows get `NULL` for the new column. |
| Type annotation `str` | Defines the Iceberg column type via Pandera → Phlo mapping. |
| No default required | Nullable columns don't need defaults for backward compatibility. |

## Step 2: Check Compatibility

Run the diff command to see how Phlo classifies the change:

```bash
phlo schema-migrate diff raw.pokemon
```

Expected output shows the change classified as a **safe widening** — adding a nullable column is always backward-compatible.

## Step 3: Generate a Migration Plan

```bash
phlo schema-migrate plan raw.pokemon
```

This generates a migration plan showing:
- The column to add (`habitat VARCHAR`)
- The change type (widening)
- The target table (`raw.pokemon`)

Review the plan before applying.

## Step 4: Apply the Migration

```bash
phlo schema-migrate apply raw.pokemon --yes
```

This widens the Iceberg table schema by adding `habitat` while preserving Phlo-managed metadata columns.

## Step 5: Re-materialize with the Updated Schema

Re-materialize on the host so the existing data is rewritten against the widened schema:

```bash
phlo materialize --select dlt_pokemon
```

The pipeline picks up the new schema, adds the column to Iceberg, and writes data with the `habitat` field populated where available.

## Step 6: Verify in Trino

Query Trino to confirm the new column exists:

```bash
phlo trino query \
  --output-format ALIGNED \
  "SELECT name, habitat FROM iceberg.raw.pokemon WHERE habitat IS NOT NULL LIMIT 5"
```

You should see Pokemon names with their habitats.

## Step 7: Check Your Work

```bash
python chapters/06-schema-evolution/check.py
```

Expected output:

```
Chapter 06 — Schema Evolution

  ✓ pokemon: 1025 rows
  ✓ pokemon has column 'habitat'

All checks passed!
```

## What You Built

You evolved a live Pandera schema by adding a nullable field, used `phlo schema-migrate` to classify the change as safe, generated a migration plan, and applied it — all without breaking existing data or downstream queries.

## Next

→ [Chapter 07 — Branch Your Data](../07-branch-your-data/)
