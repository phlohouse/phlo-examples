# Chapter 09 — Tracing & Metrics

> See your pipeline's execution traces and metrics in real time.

## What You'll Learn

- OpenTelemetry (OTEL) instrumentation in Phlo
- OTLP export configuration
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

This starts **ClickStack** (a ClickHouse-backed, all-in-one observability UI) and
the **OTEL collector**. ClickStack bundles trace storage, metric storage, and a
query UI into a single service — no need to wire up Grafana, Prometheus, and Loki
separately.

> **Note:** If you only need standalone ClickHouse without the bundled UI, the
> `phlo-clickhouse` package is available as an alternative.

### Step 2: Set OTEL Environment Variables

Add the following to `.phlo/.env.local`:

```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_SERVICE_NAME=workshop
```

| Variable | Purpose |
|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Where the SDK sends traces and metrics via OTLP/HTTP. The collector listens on port **4318**. |
| `OTEL_SERVICE_NAME` | Labels every span and metric so you can filter by service in the UI. |

### Step 3: Materialize an Asset

```bash
phlo materialize --select dlt_pokemon
```

This time the pipeline sends traces and metrics to the OTEL collector as it runs.
Each stage — DLT fetch, Iceberg write, validation — emits its own span.

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

The script verifies that ClickStack and the OTEL collector are reachable.

## Next

→ [Chapter 10 — Logs & Dashboards](../10-logs-and-dashboards/)
