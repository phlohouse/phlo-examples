# Chapter 09 — Tracing & Metrics

> See your pipeline's execution traces and metrics in real time.

## What You'll Learn

- OpenTelemetry (OTEL) instrumentation in Phlo
- Phlo observability service configuration
- Viewing traces and spans in ClickStack
- Understanding pipeline metrics

## Prerequisites

- Chapters 01–03 complete
- ~8 GB RAM available for Docker

---

## Steps

### Step 1: Start the Observability Stack

```bash
phlo services start --profile observability
```

This starts **ClickStack**, a ClickHouse-backed observability UI. The service
publishes its UI on `localhost:8123` and its ClickHouse HTTP endpoint on
`localhost:18123`.

> **Note:** If you only need standalone ClickHouse without the bundled UI, the
> `phlo-clickhouse` package is available as an alternative.

### Step 2: Confirm the Observability Ports

The workshop config sets these ports in `phlo.yaml`:

```
CLICKSTACK_PORT=8123
CLICKSTACK_HTTP_PORT=18123
```

| Variable | Purpose |
|---|---|
| `CLICKSTACK_PORT` | ClickStack UI port. |
| `CLICKSTACK_HTTP_PORT` | ClickHouse HTTP query port used by Phlo observability endpoints. |

### Step 3: Materialize an Asset

Generate traces by materializing an asset:

```bash
phlo materialize --select dlt_pokemon
```

Or use the Dagster UI — see [Chapter 1 Step 3](../01-ingest-pokemon/#step-3-materialize) for detailed UI instructions.

This gives the observability stack fresh pipeline activity to inspect.

### Step 4: Explore Traces in ClickStack

1. Open [http://localhost:8123](http://localhost:8123) in your browser.
2. Navigate to the **Traces** view.
3. Find the trace for your materialization run.
4. Click into it to see individual spans — DLT fetch, Iceberg write, validation —
   with timing and metadata.

### Step 5: Explore Metrics

Switch to the **Metrics** view in ClickStack. Look for:

- **Records processed** — counters per asset.
- **Stage durations** — how long each span took.
- **Error rates** — failures across runs.

### Step 6: Check Your Work

```bash
python chapters/09-tracing-and-metrics/check.py
```

The script verifies that the ClickStack UI and ClickHouse HTTP endpoint are reachable.

## Next

→ [Chapter 10 — Logs & Dashboards](../10-logs-and-dashboards/)
