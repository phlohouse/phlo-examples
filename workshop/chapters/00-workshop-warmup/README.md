# Chapter 00 — Workshop Warmup

> Do the expensive setup once so the rest of the workshop stays additive.

## What This Does

- Syncs the workshop environment
- Builds and starts the base stack
- Starts the observability profile
- Warms ingestion and dbt execution paths

Run it once before chapter 1 if you want the fastest subsequent chapter runs:

```bash
uv run workshop-runner --chapter 00-workshop-warmup --clean --sync
```

After that, run later chapters additively:

```bash
uv run --no-sync workshop-runner --chapter 01-ingest-pokemon
uv run --no-sync workshop-runner --chapter 02-validate-your-data
uv run --no-sync workshop-runner --chapter 11-lineage
```

OpenMetadata and Observatory are intentionally out of scope for this warmup path.
