# Chapter 14 — BI Dashboards & Named URLs

Build a Superset dashboard and access every service by name via Traefik.

## What You'll Learn

- BI dashboarding with Apache Superset — connect to Trino, build charts, save dashboards.
- Traefik reverse proxy — how `.phlo.localhost` routing works and why it matters.
- Service labels — how Phlo services register themselves with Traefik automatically.

## Prerequisites

- Chapters 01–03 complete (gold tables exist in Trino)

---

## Step 1: Start the Proxy Profile

```bash
phlo services start --profile proxy
```

This starts **Traefik** — a reverse proxy that routes `*.phlo.localhost` hostnames to the correct service. Superset is already running (it starts with the core profile).

### How `.phlo.localhost` works

Without Traefik you access services by port number: `localhost:3000` (Dagster), `localhost:8088` (Superset), `localhost:5173` (Observatory). That gets hard to remember.

Traefik maps hostnames to services:

| Hostname | Service | Direct port |
|---|---|---|
| `dagster.phlo.localhost` | Dagster | 3000 |
| `superset.phlo.localhost` | Superset | 8088 |
| `observatory.phlo.localhost` | Observatory | 5173 |
| `trino.phlo.localhost` | Trino | 8080 |
| `minio.phlo.localhost` | MinIO Console | 9001 |
| `nessie.phlo.localhost` | Nessie | 19120 |
| `traefik.phlo.localhost` | Traefik Dashboard | — |

`.phlo.localhost` subdomains resolve to `127.0.0.1` automatically — no `/etc/hosts` editing needed. The `.localhost` TLD is reserved by [RFC 6761](https://tools.ietf.org/html/rfc6761) and always resolves to your local machine.

Each Phlo service registers with Traefik via Docker labels. You don't configure routes — starting a service with `traefik.enable: "true"` makes it routable.

---

## Step 2: Open Superset

```bash
open http://localhost:8088
```

Or via Traefik:

```bash
open http://superset.phlo.localhost
```

Default credentials: **admin** / **admin**

---

## Step 3: Connect Trino as a Data Source

Superset auto-connects to Trino via a post-start hook, so the **Phlo Lakehouse** database should already exist. If not, add it manually:

In Superset → **Settings** → **Database Connections** → **+ Database**:

| Field | Value |
|---|---|
| Database type | Trino |
| SQLAlchemy URI | `trino://trino@trino:8080/iceberg` |
| Display name | Phlo Lakehouse |

> Note the host is `trino` (the Docker service name), not `localhost` — Superset connects to Trino inside the Docker network.

---

## Step 4: Create a Chart

Go to **SQL Lab** → **SQL Editor**. Select the **Phlo Lakehouse** database and run:

```sql
SELECT region, COUNT(*) AS pokemon_count
FROM gold.dim_pokemon
GROUP BY region
ORDER BY pokemon_count DESC
```

Click **Create Chart** → choose **Bar Chart** → save as **"Pokemon by Region"**.

---

## Step 5: Save to a Dashboard

Create a new dashboard called **"Pokemon Analytics"**. Drag your chart onto it. Save.

You now have a BI dashboard backed by your lakehouse — raw data from PokeAPI, transformed through dbt, visualized in Superset.

---

## Step 6: Explore the Traefik Dashboard

Open the Traefik admin UI:

```bash
open http://traefik.phlo.localhost
```

Here you can see:

- **Routers** — every hostname→service mapping that Traefik discovered from Docker labels.
- **Services** — the backend containers each router points to.
- **Entrypoints** — the ports Traefik listens on (port 80 by default).

Try a few named URLs:

```bash
# Dagster
open http://dagster.phlo.localhost

# Observatory
open http://observatory.phlo.localhost

# Trino info
curl -s http://trino.phlo.localhost/v1/info | python3 -m json.tool
```

### Troubleshooting

If port 80 is already in use, set a custom port in `.phlo/.env.local`:

```
TRAEFIK_HTTP_PORT=8880
```

Then access services with the port: `http://dagster.phlo.localhost:8880`

---

## Step 7: Check Your Work

```bash
python chapters/14-bi-dashboards-and-urls/check.py
```

Expected output:

```
Chapter 14 — BI Dashboards & Named URLs

  ✓ Superset is reachable at http://localhost:8088
  ✓ Traefik is running (traefik container healthy)
  ✓ superset.phlo.localhost is reachable via Traefik

All checks passed!
```

---

## What You Built

1. **Superset dashboard** — a chart showing Pokemon by region, backed by Trino/Iceberg gold tables.
2. **Traefik proxy** — every service accessible by name at `*.phlo.localhost`.
3. **No configuration** — services register automatically via Docker labels.

## Next

→ [Chapter 15 — Second Source with Sling](../15-second-source-with-sling/)
