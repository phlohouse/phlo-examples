# Phlo Glucose Platform Demo

A demo project showing how to build a glucose monitoring data lakehouse with Phlo.
Ingests CGM (Continuous Glucose Monitor) data from Nightscout API into an Iceberg lakehouse.

## Quick Start

### Standard Mode (installs phlo from GitHub)

```bash
cd examples/glucose-platform
phlo services init
phlo services start
```

### Development Mode (uses local phlo source)

For developing phlo itself with instant iteration:

```bash
cd examples/glucose-platform
phlo services init --dev --phlo-source /path/to/phlo
phlo services start
```

This mounts the phlo monorepo into the Dagster container and installs `phlo[defaults]` as an editable install,
so changes to phlo code are reflected after restarting Dagster:

```bash
docker restart dagster-webserver dagster-daemon
```

## Services

After starting, access:

- **Dagster UI**: http://localhost:3000 - Orchestration & monitoring
- **Trino**: http://localhost:8080 - Query engine
- **MinIO Console**: http://localhost:9101 - Object storage (minio/minio123)
- **Superset**: http://localhost:8088 - BI dashboards (admin/admin)
- **pgweb**: http://localhost:8081 - Database admin

## Project Structure

```
glucose-platform/
├── .phlo/                      # Infrastructure & generated config
│   ├── api/                   # API view definitions (NEW)
│   │   ├── views.sql          # PostgREST view SQL
│   │   ├── hasura-metadata.yaml  # Hasura tracking config
│   │   └── README.md          # API documentation
│   ├── alerting/              # Alerting configuration (NEW)
│   │   └── config.yaml        # Alert rules & destinations
│   └── dagster/               # Dagster workspace config
├── contracts/                  # Data contracts (SLAs, schema agreements)
│   └── glucose_readings.yaml
├── workflows/                  # Data workflows
│   ├── ingestion/             # Ingestion assets (@phlo_ingestion)
│   │   └── nightscout/        # Nightscout CGM data
│   │       └── readings.py    # Glucose entries ingestion
│   ├── schemas/               # Pandera validation schemas
│   │   └── nightscout.py      # Raw, Silver, Gold schemas
│   └── quality/               # Data quality checks (@phlo_quality)
│       ├── nightscout.py      # Standard quality checks
│   └── transforms/dbt/        # dbt transformation models
│       ├── bronze/           # Staging models (stg_*)
│       ├── silver/           # Fact tables (fct_*)
│       ├── gold/             # Aggregations
│       └── marts/            # BI-ready tables
│           ├── mrt_glucose_readings.sql
│           ├── mrt_glucose_overview.sql
│           └── mrt_glucose_hourly_patterns.sql
├── tests/                     # Workflow tests
├── .env.example              # Configuration template (ENHANCED)
└── pyproject.toml            # Project dependencies
```

## DLT Helper Pattern

This project demonstrates the **dedicated helper pattern** for reducing API boilerplate.

### Why Use Helpers?

When you have multiple workflows ingesting from the same API, use a dedicated helper module to:

- Avoid repeating base URL and query parameter logic
- Ensure consistency across all Nightscout workflows
- Make it easy to update API configuration in one place
- Improve code readability and maintainability

### Implementation

**Helper module** (`workflows/ingestion/nightscout/helpers.py`):

```python
from dlt.sources.rest_api import rest_api

def nightscout_api(
    resource: str,
    endpoint_path: str,
    partition_date: str | None = None,
    params: dict | None = None,
):
    """Helper to create DLT sources for Nightscout API endpoints."""
    final_params = params or {}

    # Add date range filtering if partition_date is provided
    if partition_date:
        start_time_iso = f"{partition_date}T00:00:00.000Z"
        end_time_iso = f"{partition_date}T23:59:59.999Z"
        final_params.update({
            "find[dateString][$gte]": start_time_iso,
            "find[dateString][$lt]": end_time_iso,
        })

    return rest_api(
        client={"base_url": "https://gwp-diabetes.fly.dev/api/v1"},
        resources=[{
            "name": resource,
            "endpoint": {
                "path": endpoint_path,
                "params": final_params,
            },
        }],
    )
```

**Usage in workflows** (`workflows/ingestion/nightscout/readings.py`):

```python
from phlo_dlt import phlo_ingestion
from workflows.ingestion.nightscout.helpers import nightscout_api
from workflows.schemas.nightscout import RawGlucoseEntries

@phlo_ingestion(
    table_name="glucose_entries",
    unique_key="_id",
    validation_schema=RawGlucoseEntries,
    group="nightscout",
)
def glucose_entries(partition_date: str):
    return nightscout_api(
        resource="entries",
        endpoint_path="entries.json",
        partition_date=partition_date,
        params={"count": 10000},
    )
```

### Benefits

- **Single source of truth**: Base URL and date filtering logic in one place
- **Consistency**: All workflows use the same Nightscout API configuration
- **Maintainability**: Updating the API client is a one-line change
- **Self-documenting**: Helper function signature shows available parameters

### When to Use This Pattern

Use dedicated helpers when you have:

- Multiple workflows for the same API (future: treatments, device status, profile)
- Shared date filtering or query parameters
- Common base URL and authentication
- Consistent data selection logic

See the [Developer Guide](../../phlo/docs/guides/developer-guide.md#dlt-helper-pattern-recommended) for complete documentation on this pattern.

## Materializing Assets

```bash
# Single materialization
phlo materialize glucose_entries --partition 2024-01-15

# Backfill date range
phlo backfill glucose_entries --start-date 2024-01-01 --end-date 2024-01-31

# Parallel backfill
phlo backfill glucose_entries --start-date 2024-01-01 --end-date 2024-12-31 --parallel 4

# Via Dagster UI
# Navigate to Assets > glucose_entries > Materialize
```

## Data Flow

1. **Ingestion**: `glucose_entries` fetches CGM readings from Nightscout API
2. **Bronze**: `stg_glucose_entries` stages raw data
3. **Silver**: `fct_glucose_readings` adds time dimensions & categorization
4. **Gold**: `fct_daily_glucose_metrics` computes daily aggregates & time-in-range
5. **Marts**: `mrt_glucose_*` tables ready for BI dashboards

## Merge Strategy

This project uses the **merge strategy** with **last deduplication** for glucose ingestion:

```python
@phlo_ingestion(
    table_name="glucose_entries",
    unique_key="_id",
    merge_strategy="merge",     # Upsert mode
    merge_config={"deduplication_method": "last"},  # Keep most recent reading
    ...
)
```

### Why Merge Strategy?

Glucose data from Nightscout requires merge strategy for three key reasons:

**1. Overlapping API Queries**

- Querying "last 24 hours" multiple times returns overlapping data
- Without merge, re-running a partition would create duplicates
- Merge ensures idempotent pipeline runs

**2. Retroactive Corrections**

- CGM sensors can be calibrated retroactively
- Nightscout allows editing historical glucose readings
- Merge strategy updates existing records with corrections

**3. Data Quality**

- If a pipeline fails mid-run, re-running safely completes the load
- No manual cleanup of partial data required
- `unique_key="_id"` ensures each reading appears exactly once

### Deduplication Strategy: "last"

The `merge_config={"deduplication_method": "last"}` parameter means:

- If duplicate `_id` values exist in a batch, keep the **last** occurrence
- Based on insertion order during the pipeline run
- Most appropriate for time-series data where latest reading is authoritative

### Alternative: Append Strategy

If glucose data were truly immutable (no corrections), we could use:

```python
@phlo_ingestion(
    table_name="glucose_entries",
    unique_key="_id",
    merge_strategy="append",  # Insert-only, no deduplication
    ...
)
```

**Trade-offs:**

- ✅ Faster performance (no deduplication checks)
- ❌ Duplicates if pipeline re-run
- ❌ No way to update corrected readings
- ❌ Requires careful orchestration to avoid re-runs

**Verdict**: Merge strategy is the right choice for CGM data reliability.

### Comparison Table

| Aspect          | Append Strategy | Merge Strategy (used) |
| --------------- | --------------- | --------------------- |
| **Performance** | Faster          | Slightly slower       |
| **Idempotency** | No              | Yes                   |
| **Updates**     | Not possible    | Supported             |
| **Duplicates**  | Possible        | Prevented             |
| **Use Case**    | Immutable logs  | Correctable data      |

## CLI Commands

### Core Operations

```bash
phlo services start       # Start all infrastructure
phlo services stop        # Stop infrastructure
phlo services status      # Check service health
phlo materialize <asset>  # Materialize an asset
phlo backfill <asset>     # Backfill partitions
phlo test                 # Run tests
```

### Logs & Monitoring

```bash
phlo logs                        # View recent logs
phlo logs --asset glucose_entries # Filter by asset
phlo logs --level ERROR --since 1h
phlo logs --follow               # Real-time tail

phlo metrics                     # Summary dashboard
phlo metrics asset glucose_entries
```

### Lineage & Impact Analysis

```bash
phlo lineage show glucose_entries
phlo lineage show glucose_entries --downstream
phlo lineage impact glucose_entries
```

### Schema & Catalog

```bash
phlo schema list
phlo schema show RawGlucoseEntries

phlo catalog tables
phlo catalog describe raw.glucose_entries
phlo catalog history raw.glucose_entries
```

### Data Contracts

```bash
phlo contract list
phlo contract show glucose_readings
phlo contract validate glucose_readings
```

## Data Contracts

This project includes data contracts in `contracts/` that define:

- **Schema requirements**: Required columns, types, and constraints
- **SLAs**: Freshness (2 hours), quality threshold (99%)
- **Consumers**: Teams that depend on this data

Example contract (`contracts/glucose_readings.yaml`):

```yaml
name: glucose_readings
version: 1.0.0
owner: data-team

schema:
  required_columns:
    - name: sgv
      type: integer
      constraints:
        min: 20
        max: 600

sla:
  freshness_hours: 2
  quality_threshold: 0.99

consumers:
  - name: analytics-team
    usage: BI dashboards
```

Validate contracts before deployment:

```bash
phlo contract validate glucose_readings
```

## Quality Framework

Quality checks use the `@phlo_quality` decorator and Pandera schemas:

```python
from phlo_quality import NullCheck, RangeCheck
import phlo

@phlo_quality(
    table="silver.fct_glucose_readings",
    checks=[
        NullCheck(columns=["sgv", "reading_timestamp"]),
        RangeCheck(column="sgv", min_value=20, max_value=600),
    ],
    group="nightscout",
    blocking=True,
)
def glucose_quality():
    pass
```

See `workflows/quality/nightscout.py` for the full implementation using Pandera schemas

### Schema Generation from dbt YAML

> **Key Feature**: This project demonstrates `dbt_model_to_pandera` to reduce schema duplication by 50%.
>
> Instead of maintaining separate schemas in dbt YAML and Pandera classes, we define the schema once in dbt and auto-generate the Pandera schema:
>
> ```python
> # workflows/schemas/nightscout.py
> from phlo_dbt.dbt_schema import dbt_model_to_pandera
>
> # Single source of truth: dbt YAML defines the schema
> FactGlucoseReadings = dbt_model_to_pandera(
>     "workflows/transforms/dbt/models/silver/fct_glucose_readings.yml",
>     "fct_glucose_readings"
> )
> ```
>
> **Benefits**:
> - Define schema once (in dbt YAML)
> - No schema drift between dbt and Pandera
> - dbt `data_tests` automatically become Pandera Field constraints
> - 50% less code to maintain
>
> **Implementation files**:
> - dbt schema: `workflows/transforms/dbt/models/silver/fct_glucose_readings.yml`
> - Generated Pandera: `workflows/schemas/nightscout.py` (line 63)
>
> See the [Developer Guide](../../phlo/docs/guides/developer-guide.md#approach-2-generate-schemas-from-dbt-yaml) for complete documentation.

## API Access

The glucose platform exposes data through REST and GraphQL APIs using automatically generated views from dbt marts.

### PostgREST (REST API)

Access glucose data via REST endpoints at http://localhost:3000:

```bash
# Get latest 30 days of glucose overview
curl "http://localhost:3000/api/glucose_overview?select=reading_date,avg_glucose_mg_dl,time_in_range_pct&order=reading_date.desc&limit=30"

# Get hourly patterns
curl "http://localhost:3000/api/hourly_patterns"

# Filter by time in range threshold
curl "http://localhost:3000/api/glucose_overview?time_in_range_pct=gte.70"
```

### Hasura (GraphQL API)

Query glucose data via GraphQL at http://localhost:8080:

```graphql
query GetRecentOverview {
  api_glucose_overview(order_by: { reading_date: desc }, limit: 30) {
    reading_date
    avg_glucose_mg_dl
    time_in_range_pct
    estimated_a1c_7d_avg
  }
}
```

### Regenerating API Views

When dbt models change, regenerate the API views:

```bash
# View current API views
cat .phlo/api/views.sql

# After future CLI implementation:
# phlo api generate-views --models mrt_* --apply
# phlo api hasura track --schema api
```

See `.phlo/api/README.md` for complete API documentation and examples.

## Observability

The glucose platform includes comprehensive observability features for monitoring data quality, pipeline health, and lineage.

### Metrics Dashboard

View real-time metrics about your data pipelines:

```bash
# Overall metrics summary
phlo metrics summary

# Last 7 days metrics
phlo metrics summary --period 7d

# Specific asset metrics
phlo metrics asset glucose_entries
phlo metrics asset fct_glucose_readings
```

Example metrics output:

```
Pipeline Metrics (Last 24 Hours)

Success Rate:  95.2%  (20/21 runs)
Data Processed: 14.5K rows
Avg Runtime:    3.2s (p95: 5.1s)

Top Assets by Volume:
  glucose_entries       8,640 rows
  fct_glucose_readings  8,520 rows
  fct_daily_glucose_metrics  90 rows
```

### Lineage Visualization

Understand data dependencies and impact:

```bash
# View full lineage for an asset
phlo lineage show glucose_entries

# Only downstream dependencies
phlo lineage show glucose_entries --downstream

# Impact analysis
phlo lineage impact glucose_entries
```

Example lineage tree:

```
glucose_entries
├── [upstream]
│   └── (external) Nightscout API
└── [downstream]
    ├── stg_glucose_entries (dbt)
    │   ├── fct_glucose_readings (dbt)
    │   │   ├── mrt_glucose_overview (dbt)
    │   │   └── fct_daily_glucose_metrics (dbt)
    │   └── glucose_readings_quality (check)
```

Export lineage for documentation:

```bash
# Export as Mermaid diagram
phlo lineage export --format mermaid --output docs/lineage.md

# Export as DOT for Graphviz
phlo lineage export --format dot --output lineage.dot
```

### Alerting

Configure alerts for data quality issues and pipeline failures:

```bash
# Set up Slack alerts (add to .env)
PHLO_ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK
PHLO_ALERT_SLACK_CHANNEL=#glucose-alerts

# Configure alert rules in .phlo/alerting/config.yaml
```

Alert triggers:

- Quality check failures
- Data freshness violations (> 24 hours)
- High glucose variability (CV > 40% for 7+ days)
- Pipeline materialization failures

See `.phlo/alerting/config.yaml` for alert configuration and `.env.example` for setup instructions.

## Data Catalog

The glucose platform integrates with phlo's data catalog for metadata management, schema tracking, and table lineage.

### Schema Catalog

Inspect Pandera validation schemas used in quality checks:

```bash
# List all available schemas
phlo schema list

# Show schema details
phlo schema show RawGlucoseEntries
phlo schema show FactGlucoseReadings
phlo schema show FactDailyGlucoseMetrics
```

Example schema output:

```
Schema: FactGlucoseReadings

Columns:
  entry_id              string   NOT NULL, UNIQUE
  glucose_mg_dl         int64    20-600 mg/dL, NOT NULL
  reading_timestamp     datetime NOT NULL
  direction             string   IN(Flat, SingleUp, ...)
  hour_of_day           int64    0-23, NOT NULL
  glucose_category      string   IN(hypoglycemia, in_range, ...)
  is_in_range           int64    IN(0, 1), NOT NULL

Validation Rules:
  - Glucose must be between 20-600 mg/dL
  - Hour of day must be 0-23
  - All timestamps must be valid
```

### Table Catalog

Query Iceberg table metadata:

```bash
# List all tables
phlo catalog tables

# Filter by schema
phlo catalog tables --schema raw
phlo catalog tables --schema silver

# Describe table metadata
phlo catalog describe raw.glucose_entries
phlo catalog describe silver.fct_glucose_readings

# View table history (snapshots)
phlo catalog history raw.glucose_entries --limit 10
```

Example table description:

```
Table: raw.glucose_entries
Schema: raw
Location: s3://warehouse/raw/glucose_entries
Format: Iceberg

Statistics:
  Total Files:    24
  Total Rows:     156,480
  Total Size:     12.3 MB
  Last Modified:  2024-01-15 14:30:22

Partitioning:
  - partition_date (daily)

Current Snapshot:
  Snapshot ID:  8472847294729
  Timestamp:    2024-01-15 14:30:22
  Operation:    append
```

### OpenMetadata Integration

Optionally sync metadata to OpenMetadata for catalog search and discovery:

```bash
# Configure OpenMetadata connection (add to .env)
OPENMETADATA_HOST=http://localhost:8585
OPENMETADATA_API_VERSION=v1

# Sync table metadata
phlo catalog sync --tables raw.glucose_entries
phlo catalog sync --schema silver

# Sync quality check results
phlo catalog sync --quality-checks
```

OpenMetadata provides:

- Centralized metadata search
- Data lineage visualization
- Quality check tracking
- Schema evolution history
- Column-level lineage

### Data Contracts Integration

The catalog integrates with data contracts for validation:

```bash
# Compare contract schema with actual table schema
phlo contract validate glucose_readings

# Check if contract SLAs are met
phlo contract check glucose_readings --sla
```

See `contracts/glucose_readings.yaml` for contract definitions and the Data Contracts section above for details.
