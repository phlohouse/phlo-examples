# Chapter 13 — APIs for Your Data

> Expose your gold tables via REST and GraphQL — zero application code.

## What You'll Learn

- Auto-generated REST APIs with PostgREST
- GraphQL with Hasura
- Phlo's internal API endpoints
- API profiles and service composition

## Prerequisites

Chapters 01–04 complete (gold tables published to Postgres).

---

## Step 1: Start the API Profile

```bash
phlo services start --profile api
```

This starts PostgREST, Hasura, and the Phlo API server alongside existing services.

## Step 2: Query via PostgREST (REST)

PostgREST auto-generates a REST API for every Postgres table.

```bash
curl http://localhost:3001/dim_pokemon?limit=5
```

Try filtering:

```bash
curl "http://localhost:3001/dim_pokemon?region=eq.Kanto&order=pokemon_id"
```

## Step 3: Query via Hasura (GraphQL)

Open the Hasura console:

```bash
open http://localhost:8888/console
```

Run a GraphQL query:

```graphql
query {
  dim_pokemon(limit: 5) {
    pokemon_id
    pokemon_name
    region
  }
}
```

## Step 4: Explore the Phlo API

The Phlo API provides internal endpoints for asset management:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/assets
```

## Step 5: Check Your Work

```bash
python chapters/13-apis-for-your-data/check.py
```

## Next

→ [Chapter 14 — BI Dashboards & Named URLs](../14-bi-dashboards-and-urls/)
