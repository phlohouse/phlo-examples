# Chapter 10 — Logs & Dashboards

> Collect logs in Loki, metrics in Prometheus, and visualize everything in Grafana.

## What You'll Learn

- Log aggregation with Loki
- Alloy as the log/metric collector
- Prometheus scraping and targets
- Grafana datasources, Explore view, and dashboards

## Prerequisites

Chapter 09 complete (observability profile already running).

---

## Step 1: Verify the Observability Stack

Grafana, Loki, Prometheus, and Alloy should all be running from Chapter 09's
profile start.

| Service    | URL                          |
| ---------- | ---------------------------- |
| Grafana    | <http://localhost:3100>      |
| Prometheus | <http://localhost:9090>      |
| Loki       | Accessed through Grafana     |

## Step 2: Materialize an Asset

Generate fresh logs by materializing an asset:

```bash
phlo materialize --select dlt_pokemon
```

Or use the Dagster UI — see [Chapter 1 Step 3](../01-ingest-pokemon/#step-3-materialize) for detailed UI instructions.

## Step 3: Query Logs in Grafana

Open **Grafana → Explore** and select the **Loki** datasource. Run this LogQL
query:

```
{job="phlo"}
```

You should see structured log output from the pipeline.

## Step 4: Check Prometheus Targets

Open <http://localhost:9090/targets>. See which services Prometheus is scraping.

## Step 5: Explore Pre-built Dashboards

Navigate to **Grafana → Dashboards**. Phlo ships pre-configured dashboards for
pipeline health.

## Step 6: Check Your Work

```bash
python chapters/10-logs-and-dashboards/check.py
```

## Next

→ [Chapter 11 — Lineage](../11-lineage/)
