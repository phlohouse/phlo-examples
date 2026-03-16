# Chapter 05 — Data Contracts & SLAs

Define who consumes your data and what quality guarantees they expect.

## What You'll Learn

- How `Consumer` declares downstream stakeholders — who uses your data and what they use it for.
- How `SLA` sets freshness and quality expectations — the contract your pipeline must honour.
- Wiring contracts into `@phlo_ingestion` via `consumers` and `sla` parameters.

## Prerequisites

Chapters 01–02 complete — `pokemon` table exists in Trino with validation schemas applied.

---

## Step 1: Understand Data Contracts

A **data contract** makes the relationship between data producers and consumers explicit:

| Concept | Purpose |
|---|---|
| `Consumer` | Identifies a team or system that depends on this dataset |
| `SLA` | Defines freshness, quality, and alerting expectations |

Without contracts, breaking changes go unnoticed until someone's dashboard is wrong. With contracts, Phlo can enforce guarantees and notify the right people.

## Step 2: Define Consumers and SLAs

Create `contracts/pokemon.py`:

```python
"""Pokemon data contracts."""

from phlo.contracts import Consumer, SLA

pokemon_consumer = Consumer(
    name="analytics-team",
    contact="analytics@example.com",
    usage="Pokemon type distribution reports",
)

pokemon_sla = SLA(
    freshness_hours=168,
    quality_threshold=0.95,
    notify=["analytics@example.com"],
)
```

Key points:
- `Consumer.name` — a human-readable identifier for the consuming team or service.
- `Consumer.contact` — who to reach when something breaks.
- `Consumer.usage` — documents what the consumer does with this data.
- `SLA.freshness_hours` — data must be no older than this many hours (168 = one week).
- `SLA.quality_threshold` — minimum fraction of rows that must pass validation (0.95 = 95%).
- `SLA.notify` — email addresses to alert on SLA violations.

## Step 3: Wire Contracts to Ingestion

Update `workflows/ingestion/pokemon.py` to import and attach the contracts:

```python
"""Pokemon ingestion assets with contracts."""

from phlo_dlt import phlo_ingestion
from workflows.ingestion.helpers import pokeapi
from workflows.schemas.pokemon import RawPokemon, RawPokemonTypes
from contracts.pokemon import pokemon_consumer, pokemon_sla


@phlo_ingestion(
    table_name="pokemon",
    unique_key="name",
    validation_schema=RawPokemon,
    consumers=[pokemon_consumer],
    sla=pokemon_sla,
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
    validation_schema=RawPokemonTypes,
    group="pokemon",
    cron="0 0 1 * *",
    freshness_hours=(720, 1440),
    merge_strategy="merge",
)
def pokemon_types(partition_date: str):
    """Ingest Pokemon types."""
    return pokeapi("type", limit=20)
```

Two additions to the `pokemon` asset:
- `consumers=[pokemon_consumer]` — registers the analytics team as a consumer.
- `sla=pokemon_sla` — attaches the freshness and quality contract.

## Step 4: Re-materialize and Verify

Re-materialize the Pokemon asset to pick up the contract metadata:

```bash
phlo materialize --select dlt_pokemon
```

The asset now carries contract metadata. If freshness exceeds 168 hours or quality drops below 95%, Phlo will flag a violation and notify `analytics@example.com`.

## Step 5: Check Your Work

Run the checkpoint script to verify your contracts are in place:

```bash
python chapters/05-data-contracts/check.py
```

Expected output:

```
Chapter 05 — Data Contracts & SLAs

  ✓ contracts/pokemon.py defines Consumer and SLA
  ✓ pokemon: 1025 rows (contract-backed)

All checks passed!
```

## What You Built

1. **Consumer** — declared who uses the Pokemon data and why.
2. **SLA** — set freshness (168h) and quality (95%) guarantees with email alerting.
3. **Contract-backed asset** — wired both into `@phlo_ingestion` so Phlo enforces them automatically.

Data contracts turn implicit assumptions into explicit, enforceable agreements between teams.

## Next

→ [Chapter 06 — Schema Evolution](../06-schema-evolution/)
