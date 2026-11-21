#!/usr/bin/env python3
"""Dependency-free structural validation for Maestro schemas, examples, and live snapshots."""
import json
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from maestro.engine import Maestro  # noqa: E402

SHA1 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _check_datetime(val: str) -> None:
    datetime.fromisoformat(val.replace("Z", "+00:00"))


def validate_against_schema_task(x: dict, schema: dict) -> None:
    props = schema["properties"]
    required = set(schema["required"])
    assert required <= set(x), f"task missing fields: {required - set(x)}"
    if schema.get("additionalProperties") is False:
        assert set(x) <= set(props), f"unexpected task fields: {set(x) - set(props)}"
    assert x["schema_version"] == props["schema_version"]["const"]
    assert isinstance(x["project_id"], str) and len(x["project_id"]) >= 1
    assert re.fullmatch(props["task_id"]["pattern"], x["task_id"])
    assert 1 <= len(x["title"]) <= props["title"]["maxLength"]
    assert isinstance(x["outcome"], str) and len(x["outcome"]) >= 1
    assert x["stage"] in props["stage"]["enum"]
    assert x["owner"] in props["owner"]["enum"]
    assert x["reviewer"] in props["reviewer"]["enum"]
    assert x["risk"] in props["risk"]["enum"]
    assert x["state"] in props["state"]["enum"]
    base = x["baseline"]
    b_props = props["baseline"]["properties"]
    assert set(props["baseline"]["required"]) <= set(base)
    assert set(base) <= set(b_props)
    assert base["type"] in b_props["type"]["enum"]
    assert isinstance(base["ref"], str) and base["ref"]
    if base["type"] == "git":
        assert SHA1.fullmatch(base.get("sha", ""))
    for arr in ("scope", "exclusions", "dependencies", "acceptance", "evidence_required"):
        assert isinstance(x[arr], list) and all(isinstance(v, str) for v in x[arr])
    assert len(x["scope"]) >= props["scope"]["minItems"]
    assert len(x["acceptance"]) >= props["acceptance"]["minItems"]


def validate_against_schema_handoff(x: dict, schema: dict) -> None:
    props = schema["properties"]
    required = set(schema["required"])
    assert required <= set(x), f"handoff missing fields: {required - set(x)}"
    if schema.get("additionalProperties") is False:
        assert set(x) <= set(props), f"unexpected handoff fields: {set(x) - set(props)}"
    assert x["schema_version"] == props["schema_version"]["const"]
    assert isinstance(x["project_id"], str) and x["project_id"]
    assert isinstance(x["task_id"], str) and x["task_id"]
    assert x["role"] in props["role"]["enum"]
    assert x["stage"] in props["stage"]["enum"]
    assert x["status"] in props["status"]["enum"]
    assert SHA1.fullmatch(x["base_sha"]) and SHA1.fullmatch(x["candidate_sha"])
    assert 1 <= len(x["summary"]) <= props["summary"]["maxLength"]
    assert isinstance(x["next_action"], str) and x["next_action"]
    _check_datetime(x["created_at"])

    check_schema = props["checks"]["items"]
    check_props = check_schema["properties"]
    for c in x["checks"]:
        assert set(check_schema["required"]) <= set(c)
        assert set(c) <= set(check_props), f"unexpected check keys: {set(c) - set(check_props)}"
        assert c["outcome"] in check_props["outcome"]["enum"]
        if "log_hash" in c:
            assert SHA256.fullmatch(c["log_hash"])
        if "ran_on_sha" in c:
            assert SHA1.fullmatch(c["ran_on_sha"])
        if "evidence_class" in c:
            assert c["evidence_class"] in check_props["evidence_class"]["enum"]
        if c["outcome"] in {"skipped", "not_run"}:
            assert "exit_code" not in c
        if c["outcome"] == "failed":
            assert c.get("exit_code", 0) != 0

    if x["status"] == "pass":
        assert not x["blockers"] and x["checks"]
        for c in x["checks"]:
            assert c["outcome"] == "passed" and c.get("exit_code") == 0
    if x["status"] == "blocked":
        assert x["blockers"]
    if x["status"] == "fail":
        assert any(c["outcome"] == "failed" and c.get("exit_code", 0) != 0 for c in x["checks"])


def validate_workflow_snapshot(snap: dict, schema: dict) -> None:
    props = schema["properties"]
    assert set(schema["required"]) <= set(snap)
    assert snap["stage"] in props["stage"]["enum"]
    assert snap["status"] in props["status"]["enum"]
    assert isinstance(snap["revision"], int) and snap["revision"] >= props["revision"]["minimum"]
    assert isinstance(snap["cycle"], int) and snap["cycle"] >= props["cycle"]["minimum"]
    assert (
        not isinstance(snap["progress"], bool)
        and isinstance(snap["progress"], int)
        and props["progress"]["minimum"] <= snap["progress"] <= props["progress"]["maximum"]
    )
    pkts = snap["packets"]
    assert set(props["packets"]["required"]) <= set(pkts)
    for k in props["packets"]["required"]:
        assert isinstance(pkts[k], dict)


def main() -> None:
    task_schema = load("schemas/task.schema.json")
    handoff_schema = load("schemas/handoff.schema.json")
    workflow_schema = load("schemas/workflow.schema.json")

    validate_against_schema_task(load("examples/task.example.json"), task_schema)
    print("PASS task v2: schema + stage/owner separation")

    validate_against_schema_handoff(load("examples/handoff.blocked.example.json"), handoff_schema)
    print("PASS handoff v2: schema + stage/role separation")

    with tempfile.TemporaryDirectory() as tmp:
        eng = Maestro(Path(tmp) / "contracts.sqlite3")
        for idx, (ground_path, mom_path, rep_path) in enumerate(
            (
                (
                    "examples/grounding.example.json",
                    "examples/momentum.example.json",
                    "examples/repetition.example.json",
                ),
                (
                    "examples/coding/grounding.feature.json",
                    "examples/coding/momentum.feature.json",
                    "examples/coding/repetition.feature.json",
                ),
            )
        ):
            # Separate workflow per example set so progress is independent
            w = eng.start(
                f"contracts-{idx}",
                f"contract-check-{idx}",
                "validate live packets",
            )
            validate_workflow_snapshot(w, workflow_schema)
            w = eng.ground(w["id"], w["revision"], load(ground_path))
            w = eng.begin_momentum(w["id"], w["revision"])
            w = eng.deliver(w["id"], w["revision"], load(mom_path))
            w = eng.submit_mastery(w["id"], w["revision"])
            w = eng.review(w["id"], w["revision"], "PASS", [], ["contract:verified"])
            w = eng.learn(w["id"], w["revision"], load(rep_path))
            validate_workflow_snapshot(w, workflow_schema)
    print("PASS workflow schema + all 6 stage packet examples")
    print("PASS Maestro contracts (3/3)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAIL:", e, file=sys.stderr)
        raise
