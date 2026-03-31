"""Pokemon data contracts."""

from phlo.contracts import Consumer, SLA

pokemon_consumer = Consumer(
    name="analytics-team",
    contact="analytics@example.com",
    usage="Pokemon type distribution reports",
)

pokemon_sla = SLA(
    freshness_hours=168,
    quality_threshold=0.95,
    notify=["analytics@example.com"],
)
