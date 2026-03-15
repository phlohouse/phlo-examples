"""Pokemon trading card ingestion via Sling."""

from phlo_sling import phlo_sling_replication


@phlo_sling_replication(
    stream_name="data/pokemon_cards.csv",
    table_name="pokemon_cards",
    source_conn="file://",
    target_conn="PHLO_ICEBERG",
    group="pokemon",
    mode="full-refresh",
)
def pokemon_cards(runtime):
    """Ingest Pokemon trading card prices from CSV."""
    return None
