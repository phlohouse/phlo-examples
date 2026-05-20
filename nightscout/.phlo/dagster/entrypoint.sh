#!/bin/bash
# Phlo Dagster Entrypoint
# Syncs dependencies in dev mode before running the main command

set -e

# If dev mode is enabled, sync dependencies from mounted pyproject.toml
if [ "$PHLO_DEV_MODE" = "true" ] && [ -f /opt/phlo-dev/pyproject.toml ]; then
    echo "Dev mode: syncing dependencies from pyproject.toml..."
    # Extract and install dependencies from the mounted pyproject.toml
    # Using uv pip install with --system to install into the container's Python
    cd /opt/phlo-dev
    uv pip install --system -e ".[defaults]" 2>/dev/null || \
      uv pip install --system -e . 2>/dev/null || \
      uv pip install --system . || \
      echo "Warning: Could not sync dependencies"
    cd /opt/dagster
    echo "Dev mode: dependencies synced"
fi

# In decoupled mode, runtime plugins live in /opt/phlo-dev/packages.
# Install local workspace packages so project workflows can import plugin modules.
if [ "$PHLO_DEV_MODE" = "true" ] && [ -d /opt/phlo-dev/packages ]; then
    echo "Dev mode: installing local workspace packages..."
    for pkg_dir in /opt/phlo-dev/packages/*; do
        if [ ! -d "$pkg_dir" ] || [ ! -f "$pkg_dir/pyproject.toml" ]; then
            continue
        fi
        uv pip install --system -e "$pkg_dir" || echo "Warning: Could not install $pkg_dir"
    done
    for required_pkg in \
        phlo-core-plugins \
        phlo-dagster \
        phlo-dlt \
        phlo-dbt \
        phlo-pandera \
        phlo-iceberg \
        phlo-nessie \
        phlo-trino \
        phlo-postgres \
        phlo-minio \
        phlo-lineage
    do
        required_path="/opt/phlo-dev/packages/$required_pkg"
        if [ -d "$required_path" ]; then
            uv pip install --system -e "$required_path" || echo "Warning: Could not install $required_pkg"
        fi
    done
    uv pip install --system dagster-dbt || echo "Warning: Could not install dagster-dbt"
    echo "Dev mode: local workspace packages installed"
fi

# Execute the main command
exec "$@"
