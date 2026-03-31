# Chapter 11 — Lineage

> Trace your data from source to model — column by column.

## What You'll Learn

- Column-level lineage tracking
- The lineage store and how it's populated
- Phlo's lineage CLI surfaces
- Upstream/downstream tracing

## Prerequisites

Chapters 01–03 complete (ingestion + dbt transforms).

---

## Step 1: Understand the Lineage Graph

Phlo's `phlo-lineage` package tracks how data flows through your pipeline at the
**column level**. Three key components make this work:

| Component            | Role                                                                 |
| -------------------- | -------------------------------------------------------------------- |
| `LineageStore`       | Persists lineage edges (source → target, column → column).          |
| `LineageGraph`       | Builds a directed acyclic graph (DAG) from stored edges.            |
| `dbt_column_lineage` | Extracts column-level lineage from dbt manifest artifacts.          |

When you run `phlo materialize`, dbt compiles a manifest that describes every
model, its columns, and where each column's value originates. `phlo-lineage`
parses that manifest and populates the `LineageStore` so the rest of the stack
can query it.

## Step 2: Use the Existing Lineage Graph

```bash
phlo lineage status
phlo lineage show dim_pokemon --direction upstream
```

The prerequisite chapters already ingested the raw assets and built the dbt
models. This chapter focuses on querying the lineage graph that those earlier
runs populated. Observatory is intentionally out of scope for now.

## Step 3: Inspect an Asset Lineage Graph

Inspect the upstream graph for a model in detail:

```bash
phlo lineage show dim_pokemon --direction upstream
```

You should see upstream dependencies such as `stg_pokemon` and `dlt_pokemon`.

## Step 4: Explore Overall Graph Status

Check the overall graph summary:

```bash
phlo lineage status
```

You should see counts for total assets and total dependencies in the lineage graph.

## Step 5: Trace Downstream

Analyze downstream impact from the raw asset:

```bash
phlo lineage impact dlt_pokemon
```

From there you can see every downstream asset that depends on `dlt_pokemon`:
staging models and gold-layer dimensions built on top.

## Step 6: Check Your Work

```bash
python chapters/11-lineage/check.py
```

## Next

→ [Chapter 12 — Data Catalog](../12-data-catalog/)
