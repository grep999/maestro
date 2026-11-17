#!/usr/bin/env python3
"""Dependency-free provenance checks for TRANSFORMACJA research data."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def load_json(name):
    with (DATA / name).open(encoding="utf-8") as handle:
        return json.load(handle)

with (DATA / "source_register.csv").open(encoding="utf-8-sig", newline="") as handle:
    sources = list(csv.DictReader(handle))
source_ids = {row["source_id"] for row in sources}
assert len(source_ids) == len(sources), "duplicate source_id in source register"

aggregates = load_json("privatization_aggregates.json")
assert aggregates["geography"] == "Poland"
assert aggregates["records"], "aggregate dataset is empty"
for record in aggregates["records"]:
    assert record["source_id"] in source_ids, f"unknown aggregate source: {record['source_id']}"
    assert isinstance(record["value"], (int, float)) and record["value"] >= 0
    assert record["limitations"], f"missing caveats: {record['id']}"

events = load_json("ownership_events.json")
assert events["records"], "transaction ledger is empty"
for event in events["records"]:
    assert event["event_status"] == "closed", f"non-closed event in factual ledger: {event['event_id']}"
    assert event["event_type"] in {"share_sale", "asset_sale", "lease", "liquidation", "capital_increase"}
    assert event["event_date_precision"] in {"day", "month", "year", "period"}
    assert event["event_date"], f"missing date: {event['event_id']}"
    assert event["source_ids"], f"missing sources: {event['event_id']}"
    assert set(event["source_ids"]) <= source_ids, f"unknown event source: {event['event_id']}"
    stake = event.get("stake_pct_acquired")
    assert stake is None or 0 < float(stake) <= 100, f"invalid stake: {event['event_id']}"
    assert event["confidence"] in {"A_primary_verified", "B_multiple_reliable_sources"}

with (DATA / "privatization_1990_1996.csv").open(encoding="utf-8-sig", newline="") as handle:
    periods = list(csv.DictReader(handle))
assert len(periods) == 7, "expected seven IMF periods through Jan-Sep 1996"
assert periods[-1]["period"] == "1996-01/1996-09", "1996 must remain a nine-month period"
assert all(row["source_id"] in source_ids for row in periods)

with (DATA / "research_leads.csv").open(encoding="utf-8-sig", newline="") as handle:
    leads = list(csv.DictReader(handle))
assert len(leads) >= 5
print(f"PASS: {len(sources)} sources, {len(aggregates['records'])} aggregates, "
      f"{len(periods)} IMF periods, {len(events['records'])} closed events, {len(leads)} research leads")
