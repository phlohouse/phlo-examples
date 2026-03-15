# Chapter 07 — Branch Your Data

**What you'll learn:** Git-like data versioning with Nessie — create branches, make changes in isolation, diff, and merge.

**Time:** ~15 minutes

---

## Prerequisites

- Chapters 01–02 complete (Pokemon data ingested and validated)
- Services running (`phlo services start`)

---

## Background

Nessie is a git-like catalog for your data lakehouse. Just as Git lets you branch code, Nessie lets you branch *data*:

| Git concept | Nessie equivalent |
|---|---|
| `git branch` | `phlo nessie branch create` |
| `git diff` | `phlo nessie branch diff` |
| `git merge` | `phlo nessie branch merge` |
| `git log` | Nessie commit history |

Every table in Iceberg is tracked by Nessie. When you create a branch, you get a snapshot of the entire catalog at that point in time. Changes on the branch — new tables, updated data, schema changes — are isolated until you merge.

This is powerful for:

- **Safe experimentation** — try a new ingestion or transform without affecting production
- **CI/CD for data** — validate changes on a branch before promoting to main
- **Reproducibility** — query data as it existed at any point in time

Phlo's Write-Audit-Publish (WAP) pattern uses this under the hood: every pipeline run writes to an isolated branch, validates the data, then merges to main automatically.

In this chapter you'll do it manually to see how the pieces fit together.

---

## Step 1 — List existing branches

Start by seeing what branches exist:

```bash
phlo nessie branch list
```

You should see a single `main` branch — the default reference for all catalog operations.

---

## Step 2 — Create a branch

Create an experiment branch from main:

```bash
phlo nessie branch create workshop-experiment
```

```
✓ Created branch: workshop-experiment
  From: main
  Head: a1b2c3d4
```

Verify it appears:

```bash
phlo nessie branch list
```

You should now see both `main` and `workshop-experiment`.

---

## Step 3 — Materialize to the branch

Run a materialization. Phlo's WAP pattern automatically writes to an isolated branch and merges to main, but you can also re-materialize data that will land on main:

```bash
phlo materialize --select dlt_pokemon
```

This re-ingests the Pokemon data. The WAP sensors create a temporary branch, write data, validate, then merge back to main.

> **Note:** The WAP pattern handles branch isolation automatically during materialization. The `workshop-experiment` branch you created is a separate experiment — it captured a snapshot of main at creation time.

---

## Step 4 — Diff against main

Compare your experiment branch to main:

```bash
phlo nessie branch diff workshop-experiment main
```

If you haven't made changes directly on `workshop-experiment`, the diff will show no differences — the branch was forked from the same point. After the materialization in Step 3 landed new commits on main, the diff may show tables that were modified on main since the branch was created.

---

## Step 5 — Merge the branch

Merge the experiment branch back into main:

```bash
phlo nessie branch merge workshop-experiment main
```

```
✓ Merged workshop-experiment into main
✓ Deleted source branch: workshop-experiment
```

By default, the source branch is deleted after merge (like a squash-merge). Use `--no-delete-source` to keep it, or `--dry-run` to preview without merging:

```bash
phlo nessie branch merge workshop-experiment main --dry-run
```

---

## Step 6 — Verify in Trino

Confirm the Pokemon data is available on main via Trino:

```bash
phlo trino query "SELECT COUNT(*) FROM iceberg.raw.pokemon"
```

You should see a count of 100+ rows.

---

## Step 7 — Check your work

Run the chapter checkpoint:

```bash
python chapters/07-branch-your-data/check.py
```

You should see:

```
Chapter 07 — Branch Your Data

  ✓ Nessie API is reachable
  ✓ main branch: pokemon has 151 rows

All checks passed!
```

---

## Summary

You now know:

- **Nessie** provides git-like branching for your data catalog
- `phlo nessie branch create/list/diff/merge` manage branches from the CLI
- Phlo's **WAP pattern** uses branches automatically — every pipeline run writes in isolation then merges
- You can create **manual branches** for safe experimentation and review changes before merging

## Next

→ [Chapter 08 — Alerting & the Hook Bus](../08-alerting-and-hooks/)
