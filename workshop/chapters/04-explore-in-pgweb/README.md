# Chapter 04 — Explore in PgWeb

**What you'll learn:** How Phlo uses Postgres as a serving and metadata layer, and how to browse it with PgWeb.

**Time:** ~10 minutes

---

## Background

In previous chapters you ingested data into Iceberg and transformed it with dbt running on Trino. That gives you a powerful lakehouse — but applications, APIs, and dashboards often need a relational database for fast lookups.

Phlo's pattern is:

```
Iceberg (source of truth) → dbt transform → Postgres (serving layer)
```

Postgres serves three roles in a Phlo stack:

| Role | Examples |
|---|---|
| **Metadata store** | Dagster run history, asset materializations |
| **Serving layer** | Published tables for apps, APIs, BI tools |
| **RBAC / config** | User permissions, connection settings |

PgWeb gives you a lightweight web UI to browse all of it — no psql session required.

---

## Step 1 — Recap: gold tables live in Iceberg

Your Chapter 03 dbt models created gold-layer tables in Iceberg (queried via Trino). Those remain the analytical source of truth. Postgres is the *serving* layer — a downstream consumer, not a replacement.

---

## Step 2 — Open PgWeb

PgWeb starts automatically with `phlo services start`. Open it:

```bash
open http://localhost:10008
```

You should see the PgWeb interface — a SQL editor on the left, results on the right.

### Quick tour

| Feature | Where to find it |
|---|---|
| **Table browser** | Left sidebar — expand schemas to see tables and columns |
| **SQL editor** | Centre panel — write and run queries |
| **Export** | Results toolbar — export to CSV or JSON |
| **Table info** | Click a table name → see columns, indexes, row count |

---

## Step 3 — Query Phlo metadata in Postgres

Phlo stores Dagster pipeline metadata in Postgres. Try this in PgWeb's SQL editor:

```sql
SELECT run_id, status, start_time, end_time
FROM runs
ORDER BY start_time DESC
LIMIT 5;
```

This shows your most recent Dagster runs — you should see entries from the ingestion and transform jobs in earlier chapters.

> **Tip:** Browse the `public` schema in the sidebar to see what other metadata tables Dagster maintains.

---

## Step 4 — Checkpoint

Verify PgWeb and Postgres are reachable:

```bash
python chapters/04-explore-in-pgweb/check.py
```

You should see:

```
Chapter 04 — Explore in PgWeb

  ✓ PgWeb is reachable at http://localhost:10008
  ✓ Postgres is ready

All checks passed!
```

---

## Summary

You now know:

- **Postgres** is Phlo's metadata store and lightweight serving layer
- **PgWeb** at `localhost:10008` gives you a web UI to browse tables, run queries, and export results
- Gold tables live in **Iceberg** (source of truth); Postgres is for downstream consumption

## Next

→ [Chapter 05 — Data Contracts & SLAs](../05-data-contracts/)
