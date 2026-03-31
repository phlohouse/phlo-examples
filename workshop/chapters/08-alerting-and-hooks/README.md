# Chapter 08 — Alerting & the Hook Bus

**What you'll learn:** How Phlo's hook event bus works, how to configure alert destinations, and how to send and trigger alerts from quality check failures.

**Time:** ~15 minutes

---

## Background

When a quality check fails or a pipeline errors out, you want to know about it — not discover it hours later in the Dagster UI. Phlo's **hook bus** is an event-driven system that decouples pipeline events from reactions like alerting, metrics, and logging.

Key concepts:

| Concept | What it does |
|---|---|
| **HookBus** | Central dispatcher — emits events and routes them to registered handlers by priority and filter |
| **QualityResultEvent** | Emitted after every quality check with `passed`, `check_name`, `asset_key`, and `severity` |
| **TelemetryEvent** | Emitted for structured logs and metrics — alerting triggers on `error` / `critical` levels |
| **AlertingHookPlugin** | Listens for `quality.result` and `telemetry.log` events and sends alerts via configured destinations |
| **Alert destinations** | Slack (webhook), PagerDuty (integration key), Email (SMTP) — configured via environment variables |

This is an **exploration-only** chapter — no code to write. You'll configure environment variables and run CLI commands.

---

## Prerequisites

Chapters 01–02 complete — `pokemon` table exists in Trino.

Services running:

```bash
phlo services start
```

---

## Step 1 — Understand the Hook Bus

When you run `phlo materialize`, the ingestion pipeline emits events at key lifecycle points. The `HookBus` singleton discovers hook plugins at first emit and dispatches events to matching handlers.

The flow looks like this:

```
Quality check runs
  → QualityResultEvent(passed=False, check_name="RawPokemon", asset_key="dlt_pokemon")
    → HookBus dispatches to AlertingHookPlugin
      → AlertingHookPlugin._handle_quality() maps severity and sends Alert
        → SlackAlertDestination posts to your webhook
```

The `AlertingHookPlugin` registers two handlers:

- **`alerting_quality`** — filters on `quality.result` events. If `passed=False`, it creates an `Alert` and sends it via the `AlertManager`.
- **`alerting_telemetry`** — filters on `telemetry.log` and `telemetry.metric` events. Only fires for `error` or `critical` levels.

---

## Step 2 — Configure an Alert Destination

The simplest destination is a Slack incoming webhook. Add it to your local environment:

```bash
echo 'PHLO_ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' >> .phlo/.env.local
```

Replace the URL with a real Slack webhook if you have one. Other supported variables:

```
PHLO_ALERT_SLACK_CHANNEL=#alerts                    (optional)
PHLO_ALERT_PAGERDUTY_KEY=...
PHLO_ALERT_EMAIL_SMTP_HOST=smtp.example.com
PHLO_ALERT_EMAIL_SMTP_PORT=587                      (optional, default: 587)
PHLO_ALERT_EMAIL_SMTP_USER=user@example.com
PHLO_ALERT_EMAIL_SMTP_PASSWORD=password
PHLO_ALERT_EMAIL_RECIPIENTS=team@example.com,admin@example.com
```

> **No Slack webhook?** That's fine — you can still explore the CLI commands below. They'll show "No alert destinations configured" which confirms the system is working.

---

## Step 3 — List Alert Destinations

Check what destinations are configured:

```bash
phlo alerts list
```

If you set a Slack webhook in Step 2, you'll see:

```
     Configured Alert Destinations
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Name  ┃ Type                    ┃ Status  ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ slack │ SlackAlertDestination   │ ✓ Ready │
└───────┴─────────────────────────┴─────────┘
```

If no destinations are configured, the output lists the environment variables you can set.

---

## Step 4 — Send a Test Alert

Send a test alert to verify your configuration:

```bash
phlo alerts test --severity warning
```

If a destination is configured, you'll see:

```
✓ Test alert sent successfully! Check your configured alert destinations.
```

Check your Slack channel — you should see a "🧪 Phlo Test Alert" message.

You can also check the overall alert system status:

```bash
phlo alerts status
```

---

## Step 5 — Trigger a Real Alert

To see the hook bus fire an alert from an actual quality failure, temporarily break your Pandera schema (from Chapter 02).

Edit `workflows/schemas/pokemon.py` to add an impossible constraint:

```python
class RawPokemon(PhloSchema):
    name: str = Field(ge=1, description="Pokemon name")  # ge=1 on a string — will fail
    url: str = Field(description="API URL for full details")
```

Then materialize:

```bash
phlo materialize --select dlt_pokemon
```

The validation will fail. If you have a Slack webhook configured, the `AlertingHookPlugin` catches the `QualityResultEvent(passed=False)` and sends an alert with:

- **Title:** `Quality check failed: RawPokemon`
- **Asset:** `dlt_pokemon`
- **Details:** The Pandera error message

**Fix the schema** after testing — remove `ge=1` and re-materialize to confirm it passes:

```bash
phlo materialize --select dlt_pokemon
```

---

## Step 6 — Check Your Work

```bash
python chapters/08-alerting-and-hooks/check.py
```

Expected output:

```
Chapter 08 — Alerting & the Hook Bus

  ✓ Dagster webserver is running
  ✓ pokemon table: 1025 rows (pipeline healthy)

All checks passed!
```

This confirms Dagster is running and your pipeline is still healthy after the alerting exploration.

---

## Summary

You now know:

- **HookBus** dispatches pipeline events (quality results, telemetry) to registered plugins
- **AlertingHookPlugin** converts failed quality checks into alerts sent to Slack, PagerDuty, or Email
- **`phlo alerts list`** shows configured destinations; **`phlo alerts test`** verifies they work
- Alert destinations are configured via environment variables — no code changes needed

## Next

→ [Chapter 09 — Tracing & Metrics](../09-tracing-and-metrics/)
