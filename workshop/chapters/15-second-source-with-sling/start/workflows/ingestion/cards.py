"""Pokemon trading card ingestion via Sling."""

from phlo_sling import phlo_sling_replication


# TODO: Create a Sling replication asset for pokemon_cards.csv
# Use @phlo_sling_replication with:
#   - stream_name: "data/pokemon_cards.csv"
#   - table_name: "pokemon_cards"
#   - source_conn: "file://"
#   - target_conn: "PHLO_ICEBERG"
#   - group: "pokemon"
#   - mode: "full-refresh"
#
# The decorated function should accept runtime context and can return None.
