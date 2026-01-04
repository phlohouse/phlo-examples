# Analyst DuckDB Demo

A demonstration of analyst-friendly read-only access to Phlo's Iceberg lakehouse using DuckDB.

Query your lakehouse data directly from your laptop without Docker or Python development experience.

## Overview

This example shows how data analysts can query Iceberg tables using DuckDB's `iceberg_scan()` function. It demonstrates the **analyst access pattern** for teams that need to:

- Query lakehouse data without Docker access
- Explore data locally on their laptops
- Use familiar SQL without learning complex data engineering tools
- Export results to CSV or integrate with Jupyter notebooks

**Key Benefits:**

- No Docker installation required
- No Python coding needed (pure SQL)
- Read-only access (safe exploration)
- Works with any Iceberg table in your lakehouse
- Local performance (no network query overhead)

## Prerequisites

Before using this demo, ensure you have:

1. **Existing Phlo lakehouse** with Iceberg tables created via `@phlo_ingestion` workflows
2. **DuckDB installed** on your laptop (see Installation below)
3. **Access to MinIO/S3** where Iceberg tables are stored
4. **Table metadata location** from your data engineering team

### DuckDB Installation

```bash
# Install via pip
pip install duckdb

# Or via Homebrew (macOS)
brew install duckdb

# Or download from https://duckdb.org/docs/installation/
```

Verify installation:

```bash
python3 -c "import duckdb; print(duckdb.__version__)"
```

## Quick Start

### Running the Demo Script

The included Python script demonstrates the complete workflow:

```bash
# Navigate to the demo directory
cd phlo-examples/analyst-duckdb-demo

# Run the demo
python analyst_duckdb_demo.py
```

**What it does:**

1. Checks DuckDB installation
2. Creates DuckDB connection
3. Installs Iceberg extension
4. Configures MinIO/S3 connection
5. Discovers table metadata location
6. Executes sample queries against Iceberg tables
7. Shows usage examples

### Manual SQL Workflow

For analysts who prefer pure SQL:

```python
import duckdb

# 1. Create connection
conn = duckdb.connect()

# 2. Install and load Iceberg extension
conn.execute("INSTALL iceberg")
conn.execute("LOAD iceberg")

# 3. Configure S3/MinIO connection
conn.execute("SET s3_endpoint = 'localhost:10001'")
conn.execute("SET s3_use_ssl = false")
conn.execute("SET s3_url_style = 'path'")
conn.execute("SET s3_access_key_id = 'minio'")
conn.execute("SET s3_secret_access_key = 'minio123'")

# 4. Query the table (get metadata location from data team)
metadata = 's3://lake/warehouse/raw/entries_<UUID>/metadata/<version>.metadata.json'

# Query the data
df = conn.execute(f"SELECT * FROM iceberg_scan('{metadata}') LIMIT 10").df()
print(df)
```

## Setup Guide

### Step 1: Get Table Metadata Location

The metadata location is the S3/MinIO path to your Iceberg table's metadata file.

**Ask your data engineering team** for the metadata location, or if you have Docker access:

```bash
docker compose exec dagster-webserver python -c "
from phlo_iceberg.catalog import get_catalog
table = get_catalog(ref='main').load_table('raw.entries')
print(table.metadata_location)
"
```

Example output:

```
s3://lake/warehouse/raw/entries_a1b2c3d4/metadata/00042-e5f6g7h8.metadata.json
```

### Step 2: Configure MinIO Credentials

Get credentials from your `.env` file or data engineering team:

```bash
# From your lakehouse project directory
cat .env | grep MINIO
```

You'll need:

- `MINIO_HOST` (default: localhost)
- `MINIO_API_PORT` (default: 10001)
- `MINIO_ROOT_USER` (default: minio)
- `MINIO_ROOT_PASSWORD` (default: minio123)

### Step 3: Test Connection

```python
import duckdb

conn = duckdb.connect()
conn.execute("INSTALL iceberg; LOAD iceberg")

# Test MinIO connection
conn.execute("SET s3_endpoint = 'localhost:10001'")
conn.execute("SET s3_use_ssl = false")
conn.execute("SET s3_url_style = 'path'")
conn.execute("SET s3_access_key_id = 'minio'")
conn.execute("SET s3_secret_access_key = 'minio123'")

# Test query (replace with actual metadata location)
result = conn.execute(f"SELECT COUNT(*) FROM iceberg_scan('{metadata_location}')").fetchone()
print(f"Total rows: {result[0]:,}")
```

## Usage Examples

### Example 1: Count Total Rows

```python
import duckdb

conn = duckdb.connect()
conn.execute("INSTALL iceberg; LOAD iceberg")

# Configure S3
conn.execute("SET s3_endpoint = 'localhost:10001'")
conn.execute("SET s3_use_ssl = false")
conn.execute("SET s3_url_style = 'path'")
conn.execute("SET s3_access_key_id = 'minio'")
conn.execute("SET s3_secret_access_key = 'minio123'")

# Query
metadata = 's3://lake/warehouse/raw/entries_<UUID>/metadata/<version>.metadata.json'
result = conn.execute(f"SELECT COUNT(*) as total FROM iceberg_scan('{metadata}')").fetchone()
print(f"Total rows: {result[0]:,}")
```

### Example 2: Date Range Analysis

```python
# Get min/max dates and distinct days
query = f"""
SELECT
    MIN(date) as first_reading,
    MAX(date) as last_reading,
    COUNT(DISTINCT date_string::DATE) as distinct_days,
    COUNT(*) as total_readings
FROM iceberg_scan('{metadata}')
"""

result = conn.execute(query).df()
print(result)
```

### Example 3: Sample Recent Data

```python
# Get latest 10 records
query = f"""
SELECT
    date_string,
    sgv,
    direction,
    device
FROM iceberg_scan('{metadata}')
ORDER BY date DESC
LIMIT 10
"""

df = conn.execute(query).df()
print(df)
```

### Example 4: Daily Aggregations

```python
# Calculate daily statistics for last 7 days
query = f"""
WITH max_date AS (
    SELECT MAX(date) as max_dt
    FROM iceberg_scan('{metadata}')
)
SELECT
    date_string::DATE as day,
    COUNT(*) as readings,
    ROUND(AVG(sgv), 1) as avg_glucose,
    MIN(sgv) as min_glucose,
    MAX(sgv) as max_glucose
FROM iceberg_scan('{metadata}')
CROSS JOIN max_date
WHERE date >= max_dt - (7 * 24 * 60 * 60 * 1000)  -- 7 days in milliseconds
  AND sgv IS NOT NULL
GROUP BY date_string::DATE
ORDER BY day DESC
"""

df = conn.execute(query).df()
print(df)
```

### Example 5: Export to CSV

```python
# Export query results to CSV for Excel/Tableau
query = f"""
COPY (
    SELECT
        date_string::DATE as day,
        AVG(sgv) as avg_glucose,
        COUNT(*) as reading_count
    FROM iceberg_scan('{metadata}')
    GROUP BY date_string::DATE
    ORDER BY day DESC
) TO 'glucose_daily_summary.csv' (HEADER, DELIMITER ',')
"""

conn.execute(query)
print("Exported to glucose_daily_summary.csv")
```

## Common Use Cases

### Jupyter Notebook Integration

```python
# In a Jupyter notebook
import duckdb
import matplotlib.pyplot as plt

conn = duckdb.connect()
conn.execute("INSTALL iceberg; LOAD iceberg")

# Configure connection (same as above)
# ...

# Query and visualize
df = conn.execute(f"""
    SELECT
        date_string::DATE as date,
        AVG(sgv) as avg_glucose
    FROM iceberg_scan('{metadata}')
    GROUP BY date_string::DATE
    ORDER BY date
""").df()

# Plot
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['avg_glucose'])
plt.title('Average Daily Glucose')
plt.xlabel('Date')
plt.ylabel('Glucose (mg/dL)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### Connecting to Multiple Tables

```python
# Query multiple table layers
raw_metadata = 's3://lake/warehouse/raw/entries_<UUID>/metadata/<version>.metadata.json'
silver_metadata = 's3://lake/warehouse/silver/fct_glucose_readings_<UUID>/metadata/<version>.metadata.json'

# Join tables
query = f"""
SELECT
    r.date_string,
    r.sgv as raw_glucose,
    s.glucose_mg_dl as silver_glucose,
    s.glucose_category
FROM iceberg_scan('{raw_metadata}') r
JOIN iceberg_scan('{silver_metadata}') s
    ON r._id = s.entry_id
WHERE r.date >= CURRENT_TIMESTAMP - INTERVAL 1 DAY
LIMIT 100
"""

df = conn.execute(query).df()
print(df)
```

## When to Use DuckDB vs Trino vs Superset

Different tools serve different analyst needs. Here's when to use each:

### Comparison Table

| Feature | DuckDB | Trino | Superset |
|---------|--------|-------|----------|
| **Use Case** | Ad-hoc exploration | Complex SQL analytics | BI dashboards |
| **Installation** | Local only | Docker required | Docker required |
| **Query Language** | SQL | SQL | Visual + SQL |
| **Performance** | Local data | Distributed queries | Pre-computed |
| **Access Pattern** | Read-only files | Full catalog | View layer |
| **Best For** | Quick analysis | Complex joins | Stakeholder reports |
| **Data Export** | CSV, Parquet, Excel | Yes | Limited |
| **Visualizations** | None (use Jupyter) | None | Built-in |
| **Collaboration** | Share notebooks | Shared queries | Shared dashboards |
| **Learning Curve** | Low | Medium | Low |

### Use DuckDB When:

- You need quick, ad-hoc exploration on your laptop
- You want to avoid Docker or server access
- You're analyzing a single table or small joins
- You need to export results to CSV/Excel
- You're prototyping queries before adding to pipelines
- You want to use Jupyter notebooks locally

### Use Trino When:

- You need to query multiple large tables with complex joins
- You're running production-grade analytics queries
- You need distributed query performance
- You're joining data across different schemas (raw, silver, gold)
- You need full SQL analytics capabilities
- You have Docker access

### Use Superset When:

- You're building dashboards for stakeholders
- You need visualizations (charts, graphs)
- You want to share insights with non-technical users
- You need scheduled reports
- You're creating recurring analytics
- You have Docker access

### Recommended Workflow

**Exploration phase:**
1. Use DuckDB for initial data exploration
2. Prototype queries locally
3. Validate assumptions

**Analysis phase:**
1. Move complex queries to Trino for performance
2. Join multiple tables efficiently
3. Create materialized views if needed

**Reporting phase:**
1. Build Superset dashboards from Trino queries
2. Share with stakeholders
3. Schedule automated refreshes

## Limitations

**DuckDB is read-only for Iceberg tables:**

- Cannot INSERT, UPDATE, or DELETE
- Cannot create new Iceberg tables
- No write-audit-publish workflow
- No data quality enforcement

**For write operations**, use Phlo's `@phlo_ingestion` workflows.

**Performance considerations:**

- DuckDB loads metadata locally, so very large tables may be slow
- For large-scale analytics (100M+ rows), use Trino instead
- DuckDB excels at single-table queries and small joins

**No catalog integration:**

- Must manually specify metadata locations
- No automatic table discovery
- Cannot use Nessie catalog features (branching, tagging)

## Troubleshooting

### Error: "Could not open file"

```
Error: Could not open file 's3://lake/warehouse/...'
```

**Solution:** Check S3/MinIO credentials and endpoint:

```python
# Verify settings
conn.execute("SELECT current_setting('s3_endpoint')").fetchone()
conn.execute("SELECT current_setting('s3_access_key_id')").fetchone()
```

### Error: "Iceberg extension not found"

```
Error: Extension "iceberg" not found
```

**Solution:** Install the Iceberg extension:

```python
conn.execute("INSTALL iceberg")
conn.execute("LOAD iceberg")
```

### Error: "Metadata file not found"

```
Error: Metadata file does not exist
```

**Solution:** Get the latest metadata location from your data team. Metadata files are versioned and change after each write operation.

### Empty Results

If queries return no rows:

1. Verify the table has data (check in Trino or Dagster)
2. Check partition filters (date ranges)
3. Confirm you're using the latest metadata version

## Next Steps

**For Analysts:**
- Integrate with Jupyter notebooks for visualization
- Export results to Tableau/Excel
- Create reusable query templates
- Build local dashboards with Streamlit

**For Data Engineers:**
- Document table metadata locations for analysts
- Create analyst-friendly views in Silver/Gold layers
- Set up read-only S3 credentials
- Build self-service catalog with metadata locations

**Advanced Usage:**
- Query Iceberg time travel: `iceberg_scan('...', version_as_of => 42)`
- Use DuckDB's PIVOT for reshaping data
- Combine with DuckDB spatial extension for geospatial analysis
- Integrate with dbt for local model development

## Documentation

- [DuckDB Iceberg Extension](https://duckdb.org/docs/extensions/iceberg.html)
- [Phlo Documentation](https://github.com/iamgp/phlo)
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [Apache Iceberg Spec](https://iceberg.apache.org/spec/)

## Why This Example Matters

Most data lakehouse examples assume analysts have:
- Docker access
- Python development experience
- Knowledge of complex data engineering tools

This example shows how to **democratize data access** for:
- Business analysts who know SQL
- Data scientists who prefer notebooks
- Stakeholders who need quick answers
- Teams without engineering resources

Use DuckDB as the **bridge** between your lakehouse and analyst tools.
