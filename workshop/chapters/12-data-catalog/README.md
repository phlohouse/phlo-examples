# Chapter 12 — Data Catalog

**What you'll learn:** Register your tables in OpenMetadata with descriptions, owners, and tags — and see how Phlo syncs dbt metadata automatically.

**Time:** ~15 minutes

---

## Background

A data catalog is the metadata layer that makes your data discoverable and trustworthy. Without one, tables are just names — nobody knows what `dim_pokemon` contains, who owns it, or whether it's safe to use in production.

**OpenMetadata** is an open-source catalog that Phlo integrates with via the `phlo-openmetadata` package. Key concepts:

| Concept | What it does |
|---|---|
| **Data Assets** | Tables, topics, dashboards — anything OpenMetadata can catalog |
| **Descriptions** | Column-level and table-level docs synced from dbt |
| **Owners** | People or teams responsible for a data asset |
| **Tags** | Classification labels like `gold-layer`, `pii`, `pokemon` |
| **Lineage** | Visual graph of how data flows from source to destination |

This is an **exploration-only** chapter — no code to write. You'll start the catalog profile and explore the OpenMetadata UI.

---

## Prerequisites

Chapters 01–03 complete — tables exist in Trino with dbt models built.

~8 GB RAM available for Docker — the catalog profile adds the OpenMetadata server and its dependencies.

---

## Step 1 — Start the Catalog Profile

```bash
phlo services start --profile openmetadata
```

This starts OpenMetadata alongside the existing services. It can take 1–2 minutes to initialize — OpenMetadata runs database migrations on first boot.

Check it's healthy:

```bash
phlo services status
```

You should see `openmetadata-server` in the service list.

---

## Step 2 — Open OpenMetadata

```bash
open http://localhost:8585
```

Default credentials: **admin** / **admin**

You'll land on the OpenMetadata home page. The left sidebar gives you access to Data Assets, Glossary, Tags, and more.

---

## Step 3 — Explore the Data Catalog

Navigate to **Data Assets** in the left sidebar. You should see your Trino/Iceberg tables listed — the ones you built in earlier chapters.

Click on **`dim_pokemon`** and explore:

- **Schema tab** — column names, types, and descriptions populated from dbt
- **Lineage tab** — visual graph showing how `dim_pokemon` is derived from upstream sources
- **Profile tab** — data profiling stats (row counts, null percentages) if profiling has run

Column descriptions come directly from your dbt `schema.yml` files. Phlo syncs these automatically so your catalog stays in sync with your transformation layer.

---

## Step 4 — Add Owners and Tags

Governance metadata makes tables discoverable and accountable.

**Add an owner:**

1. Open `dim_pokemon` in the catalog
2. Click the **Owner** field (or the "+" next to it)
3. Assign yourself or the `admin` user

**Add tags:**

1. On the same table page, click **Add Tag**
2. Create or select tags like `pokemon`, `gold-layer`, `curated`
3. You can also tag individual columns (e.g., tag `name` as `business-key`)

Tags and owners are stored in OpenMetadata's metadata store — they persist across service restarts.

---

## Step 5 — dbt Metadata Sync

Phlo automatically syncs dbt metadata to OpenMetadata via hooks. Here's how it works:

1. **dbt models** define descriptions in `schema.yml` — table-level and column-level
2. **Phlo's OpenMetadata hook** reads the dbt manifest after compilation
3. **Descriptions, tags, and column docs** are pushed to the OpenMetadata API
4. **The catalog stays current** every time you run `phlo materialize`

This means you write docs once (in dbt) and they appear everywhere — in the catalog, in query tools, and in governance reports.

To see this in action, check that your dbt column descriptions match what's displayed in OpenMetadata for `dim_pokemon`.

---

## Step 6 — Check Your Work

```bash
python chapters/12-data-catalog/check.py
```

Expected output:

```
Chapter 12 — Data Catalog

  ✓ OpenMetadata is reachable (version 1.x.x)
  ✓ OpenMetadata has N+ table(s) cataloged

All checks passed!
```

---

## Summary

You now know:

- **OpenMetadata** provides a searchable catalog for all your data assets
- **dbt descriptions** sync automatically — write docs once, see them everywhere
- **Owners and tags** add governance metadata that makes tables discoverable and accountable
- **`phlo services start --profile openmetadata`** is all you need to add cataloging to your stack

## Next

→ [Chapter 13 — APIs for Your Data](../13-apis-for-your-data/)
