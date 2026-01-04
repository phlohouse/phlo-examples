"""Helper functions for Nightscout API ingestion.

This is project-specific code to reduce repetition across Nightscout workflows.
"""

from __future__ import annotations

from typing import Any

from dlt.sources.rest_api import rest_api


def nightscout_api(
    resource: str,
    endpoint_path: str,
    partition_date: str | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    """
    Helper to create DLT sources for Nightscout API endpoints.

    Reduces repetition across Nightscout ingestion workflows in this project.

    Args:
        resource: DLT resource name
        endpoint_path: Nightscout API path (e.g., "entries.json")
        partition_date: Date partition in YYYY-MM-DD format (optional)
        params: Additional query parameters

    Returns:
        DLT rest_api source
    """
    final_params = params or {}

    # Add date range filtering if partition_date is provided
    if partition_date:
        start_time_iso = f"{partition_date}T00:00:00.000Z"
        end_time_iso = f"{partition_date}T23:59:59.999Z"
        final_params.update(
            {
                "find[dateString][$gte]": start_time_iso,
                "find[dateString][$lt]": end_time_iso,
            }
        )

    return rest_api(
        client={
            "base_url": "https://gwp-diabetes.fly.dev/api/v1",
        },
        resources=[
            {
                "name": resource,
                "endpoint": {
                    "path": endpoint_path,
                    "params": final_params,
                },
            }
        ],
    )
