# Phlo Workshop

**Build a Pokemon lakehouse from scratch — 16 guided chapters covering every Phlo package.**

## What You'll Build

A complete data platform that:

1. Ingests Pokemon data from [PokeAPI](https://pokeapi.co/) and trading card prices from CSV
2. Transforms through bronze → silver → gold medallion layers
3. Validates with Pandera quality checks at every stage
4. Tracks end-to-end lineage across sources and transforms
5. Exposes data via REST and GraphQL APIs
6. Visualizes everything in Grafana and Superset dashboards

By the end you'll have used all 32 Phlo packages in a single, working project.

## How It Works

Each chapter follows the same pattern:

- **`start/`** — Starter files with `# TODO` annotations marking what you need to write
- **`solution/`** — Complete reference implementation
- **`check.py`** — Automated pass/fail validation you can run after each chapter

Fill in the TODOs, run the commands from the chapter README, then verify:

```bash
python 01_ingest_pokemon/check.py
```

Every chapter builds on the last — one project, progressive complexity. No throwaway
exercises.

## Prerequisites

| Requirement              | Minimum       |
| ------------------------ | ------------- |
| Docker + Docker Compose  | v24+          |
| Python                   | 3.11+         |
| uv                       | latest        |
| RAM                      | ~4 GB (Acts I–II), ~8 GB (full stack) |

## Quick Start

```bash
cd phlo-examples/workshop
uv sync --all-extras
phlo services init
phlo services start
```

Services take ~60 seconds to come up. Dagster UI will be available at
`http://localhost:10006`.

For the standalone runner, do the expensive setup once in chapter 0:

```bash
uv run workshop-runner --chapter 00-workshop-warmup --clean --sync
```

After that, run later chapters additively without resetting the stack:

```bash
uv run workshop-runner --chapter 01-ingest-pokemon
uv run workshop-runner --chapter 02-validate-your-data
uv run workshop-runner --act 2
```

## Chapter Overview

### Act I — Build a Pipeline

| Ch | Title                | Packages                                                        | Time   |
| -- | -------------------- | --------------------------------------------------------------- | ------ |
| 01 | Ingest Pokemon       | `phlo-dlt`, `phlo-minio`, `phlo-iceberg`, `phlo-trino`, `phlo-dagster` | ~15 min |
| 02 | Validate Your Data   | `phlo-pandera`                                                  | ~10 min |
| 03 | Transform with dbt   | `phlo-dbt`                                                      | ~15 min |
| 04 | Explore in PgWeb     | `phlo-postgres`, `phlo-pgweb`                                   | ~10 min |

### Act II — Make It Production-Ready

| Ch | Title                | Packages                                      | Time   |
| -- | -------------------- | --------------------------------------------- | ------ |
| 05 | Data Contracts & SLAs | core contracts                               | ~10 min |
| 06 | Schema Evolution     | core migrations, schema registry              | ~15 min |
| 07 | Branch Your Data     | `phlo-nessie`                                 | ~10 min |
| 08 | Alerting & Hooks     | `phlo-alerting`                               | ~10 min |

### Act III — Observe & Govern

| Ch | Title                | Packages                                                           | Time   |
| -- | -------------------- | ------------------------------------------------------------------ | ------ |
| 00 | Workshop Warmup      | base services, Dagster build cache, observability warmup           | ~10 min |
| 09 | Tracing & Metrics    | `phlo-otel`, `phlo-clickstack`                                     | ~15 min |
| 10 | Logs & Dashboards    | `phlo-loki`, `phlo-alloy`, `phlo-prometheus`, `phlo-grafana`       | ~15 min |
| 11 | Lineage              | `phlo-lineage`                                                     | ~10 min |
| 12 | Data Catalog         | `phlo-openmetadata`                                                | ~15 min |

### Act IV — Extend & Scale

| Ch | Title                       | Packages                                                                                   | Time   |
| -- | --------------------------- | ------------------------------------------------------------------------------------------ | ------ |
| 13 | APIs for Your Data          | `phlo-postgrest`, `phlo-hasura`, `phlo-api`                                                | ~15 min |
| 14 | BI Dashboards & Named URLs  | `phlo-superset`, `phlo-traefik`                                                            | ~15 min |
| 15 | Second Source with Sling    | `phlo-sling`                                                                               | ~10 min |
| 16 | Build Your Own Plugin       | `phlo-delta`, `phlo-rustfs`, `phlo-testing`, `phlo-core-plugins`, `phlo-observatory-example` | ~30 min |

**Total: ~3.5 hours** (or spread across multiple sessions — each act is self-contained
once its services are running).

## Validation

Run every chapter's checks in one shot:

```bash
uv run workshop-runner
```

Run a deterministic clean pass:

```bash
uv run workshop-runner --clean --sync
```

Compatibility shim:

```bash
uv run python validate_all.py
```

This executes each `check.py` in order and prints a summary:

```
✓ 01_ingest_pokemon
✓ 02_validate_data
✓ 03_transform_dbt
✗ 04_explore_pgweb — assertion failed: expected 3 tables, found 0
...
```

Useful for verifying the full workshop end-to-end or confirming nothing broke after
changes.

## Getting Help

- **Phlo docs**: [github.com/phlohouse/phlo](https://github.com/phlohouse/phlo)
- **Each chapter README** cross-references the relevant Phlo guides and package docs
- **Stuck on a TODO?** Check the `solution/` folder in that chapter — every file has a
  working reference implementation
