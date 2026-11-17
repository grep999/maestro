#!/usr/bin/env python3
"""Dependency-free structural validation for Maestro v2 packets."""
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHA=re.compile(r"^[0-9a-f]{40}$")
STAGES={"GROUNDING","MOMENTUM","MASTERY","REPETITION"}
ROLES={"ORCHESTRATOR","ARCHITECT","RESEARCHER","BUILDER","INDEPENDENT_REVIEWER","DOMAIN_SPECIALIST"}
STATES={"INBOX","GROUNDED","READY","IN_PROGRESS","VERIFYING","REVIEW","ACCEPTED","BLOCKED","REWORK","DEFERRED","REJECTED","SUPERSEDED"}
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def validate_task(x):
    required={"schema_version","project_id","task_id","title","outcome","baseline","stage","owner","reviewer","scope","exclusions","dependencies","acceptance","evidence_required","risk","state"}
    assert set(x)==required, f"task fields differ: {set(x)^required}"
    assert x["schema_version"]==2 and x["project_id"] and x["task_id"] and x["title"] and x["outcome"]
    assert x["stage"] in STAGES and x["owner"] in ROLES|{"HUMAN"}
    assert x["reviewer"] in {"INDEPENDENT_REVIEWER","HUMAN"}
    assert x["baseline"]["type"] in {"git","document","artifact","external"} and x["baseline"]["ref"]
    if x["baseline"]["type"]=="git": assert SHA.fullmatch(x["baseline"].get("sha",""))
    assert x["scope"] and x["acceptance"] and x["risk"] in {"R0","R1","R2","R3"} and x["state"] in STATES
def validate_handoff(x):
    required={"schema_version","project_id","task_id","role","stage","status","base_sha","candidate_sha","summary","changed_paths","checks","blockers","known_risks","next_action","created_at"}
    assert set(x)==required, f"handoff fields differ: {set(x)^required}"
    assert x["schema_version"]==2 and x["project_id"] and x["task_id"]
    assert x["role"] in ROLES and x["stage"] in STAGES
    assert x["status"] in {"pass","fail","blocked","conditional"}
    assert SHA.fullmatch(x["base_sha"]) and SHA.fullmatch(x["candidate_sha"])
    assert x["summary"] and x["next_action"]
    if x["status"]=="pass":
        assert not x["blockers"] and x["checks"]
        for c in x["checks"]: assert c["outcome"]=="passed" and c.get("exit_code")==0
    if x["status"]=="blocked": assert x["blockers"]
    if x["status"]=="fail": assert any(c["outcome"]=="failed" and c.get("exit_code",0)!=0 for c in x["checks"])
    for c in x["checks"]:
        if c["outcome"] in {"skipped","not_run"}: assert "exit_code" not in c
        if c["outcome"]=="failed": assert c.get("exit_code",0)!=0
def main():
    validate_task(load("examples/task.example.json")); print("PASS task v2: stage and owner are separate")
    validate_handoff(load("examples/handoff.blocked.example.json")); print("PASS handoff v2: stage and role are separate")
    w=load("schemas/workflow.schema.json")
    assert w["properties"]["stage"]["enum"]==["GROUNDING","MOMENTUM","MASTERY","REPETITION"]
    assert w["properties"]["cycle"]["minimum"]==1 and w["properties"]["progress"]["maximum"]==100
    print("PASS workflow schema: cycle and objective progress are distinct")
    print("PASS Maestro contracts (3/3)")
if __name__=="__main__":
    try: main()
    except Exception as e: print("FAIL:",e,file=sys.stderr); raise
