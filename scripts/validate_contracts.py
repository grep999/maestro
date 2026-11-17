#!/usr/bin/env python3
"""Dependency-free structural validator for Maestro example packets."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r"^[0-9a-f]{40}$")
TASK_STATES = {"INBOX", "GROUNDED", "READY", "IN_PROGRESS", "VERIFYING", "REVIEW", "ACCEPTED", "BLOCKED", "REWORK", "DEFERRED", "REJECTED", "SUPERSEDED"}
ROLES = {"grounding", "momentum", "mastery", "orchestrator"}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate_task(x):
    required = {"schema_version", "project_id", "task_id", "title", "outcome", "baseline", "owner", "reviewer", "scope", "exclusions", "dependencies", "acceptance", "evidence_required", "risk", "state"}
    assert set(x) == required, f"task fields differ: {set(x) ^ required}"
    assert x["schema_version"] == 1 and x["project_id"] and x["task_id"]
    assert x["baseline"]["type"] in {"git", "document", "artifact", "external"}
    assert x["baseline"]["ref"]
    if x["baseline"]["type"] == "git":
        assert SHA.fullmatch(x["baseline"].get("sha", "")), "git baseline requires exact SHA"
    assert x["owner"] in ROLES | {"human"}
    assert x["reviewer"] in {"grounding", "mastery", "human"}
    assert x["acceptance"] and x["state"] in TASK_STATES


def validate_handoff(x):
    required = {"schema_version", "project_id", "task_id", "role", "status", "base_sha", "candidate_sha", "summary", "changed_paths", "checks", "blockers", "known_risks", "next_action", "created_at"}
    assert set(x) == required, f"handoff fields differ: {set(x) ^ required}"
    assert x["schema_version"] == 1 and x["project_id"] and x["task_id"]
    assert x["role"] in ROLES
    assert x["status"] in {"pass", "fail", "blocked", "conditional"}
    assert SHA.fullmatch(x["base_sha"]) and SHA.fullmatch(x["candidate_sha"])
    if x["status"] == "pass":
        assert not x["blockers"], "PASS cannot contain blockers"
        assert x["checks"], "PASS requires checks"
        for check in x["checks"]:
            assert check["outcome"] == "passed", "PASS requires every check passed"
            assert check.get("exit_code") == 0, "PASS requires exit code 0"
    if x["status"] == "blocked":
        assert x["blockers"], "BLOCKED requires an explicit blocker"
    assert x["summary"] and x["next_action"] and x["created_at"]


def main():
    validate_task(load("examples/task.example.json"))
    print("PASS task packet structure")
    validate_handoff(load("examples/handoff.blocked.example.json"))
    print("PASS blocked handoff structure")
    print("PASS Maestro contract examples (2/2)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
