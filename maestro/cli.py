"""Command-line interface for the Maestro workflow control plane."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .adapters import AdapterError, get_registry
from .checks import GateRunner
from .coding import coding_seed_work, coding_start
from .engine import Maestro, WorkflowError


def packet(value: str) -> dict:
    p = Path(value)
    try:
        is_file = p.is_file()
    except OSError:
        is_file = False
    if is_file:
        raw = p.read_text(encoding="utf-8")
    else:
        if (
            value.endswith(".json")
            or "/" in value
            or "\\" in value
        ) and not value.lstrip().startswith("{"):
            raise WorkflowError(f"packet file not found: {value}")
        raw = value
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise WorkflowError("packet must be a JSON object")
    return obj


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="maestro",
        description="Project-agnostic workflow orchestration",
    )
    p.add_argument("--db", default=".maestro/state.sqlite3")
    s = p.add_subparsers(dest="cmd", required=True)

    x = s.add_parser("start")
    x.add_argument("project_id")
    x.add_argument("title")
    x.add_argument("objective")
    x.add_argument("--baseline")
    x.add_argument("--actor", default="human")
    x.add_argument("--require-verified", action="store_true")

    x = s.add_parser("coding-start")
    x.add_argument("project_id")
    x.add_argument("title")
    x.add_argument("objective")
    x.add_argument("--workspace", default=".")
    x.add_argument("--risk", default="R1", choices=["R0", "R1", "R2", "R3"])
    x.add_argument("--actor", default="human")

    x = s.add_parser("coding-seed-work")
    x.add_argument("wid")
    x.add_argument("--revision", type=int, required=True)
    x.add_argument("--actor", default="orchestrator")

    x = s.add_parser("show")
    x.add_argument("wid")

    x = s.add_parser("list")
    x.add_argument("--project")

    for cmd, default_actor in (
        ("ground", "orchestrator"),
        ("deliver", "builder"),
        ("learn", "orchestrator"),
    ):
        x = s.add_parser(cmd)
        x.add_argument("wid")
        x.add_argument("packet")
        x.add_argument("--revision", type=int, required=True)
        x.add_argument("--actor", default=default_actor)

    for cmd in ("begin-momentum", "submit-mastery", "unblock"):
        x = s.add_parser(cmd)
        x.add_argument("wid")
        x.add_argument("--revision", type=int, required=True)
        x.add_argument("--actor", default="orchestrator")

    x = s.add_parser("review")
    x.add_argument("wid")
    x.add_argument("verdict", choices=["PASS", "FAIL", "BLOCKED", "CONDITIONAL"])
    x.add_argument("--revision", type=int, required=True)
    x.add_argument("--findings", default="[]")
    x.add_argument("--evidence", default="[]")
    x.add_argument("--actor", default="independent_reviewer")
    x.add_argument("--candidate-ref")
    x.add_argument("--require-verified", action="store_true", default=None)

    x = s.add_parser("cancel")
    x.add_argument("wid")
    x.add_argument("reason")
    x.add_argument("--revision", type=int, required=True)
    x.add_argument("--actor", default="human")

    x = s.add_parser("add-work")
    x.add_argument("wid")
    x.add_argument("title")
    x.add_argument("outcome")
    x.add_argument("role")
    x.add_argument("--acceptance", required=True)
    x.add_argument("--dependencies", default="[]")
    x.add_argument("--revision", type=int, required=True)
    x.add_argument("--actor", default="orchestrator")

    x = s.add_parser("start-work")
    x.add_argument("wid")
    x.add_argument("item")
    x.add_argument("--revision", type=int, required=True)
    x.add_argument("--actor", default="human")

    x = s.add_parser("complete-work")
    x.add_argument("wid")
    x.add_argument("item")
    x.add_argument("--revision", type=int, required=True)
    x.add_argument("--evidence", required=True)
    x.add_argument("--actor", default="human")

    x = s.add_parser("work-items")
    x.add_argument("wid")

    x = s.add_parser("assign")
    x.add_argument("wid")
    x.add_argument("role")
    x.add_argument("capability")
    x.add_argument("packet")
    x.add_argument("--actor", default="orchestrator")

    x = s.add_parser("assignment")
    x.add_argument("aid")
    x.add_argument("status", choices=["ACCEPTED", "RUNNING", "RETURNED", "CANCELLED"])
    x.add_argument("--result")
    x.add_argument("--actor", default="orchestrator")

    x = s.add_parser("assignments")
    x.add_argument("wid")

    x = s.add_parser("events")
    x.add_argument("wid")

    s.add_parser("adapters")

    x = s.add_parser("adapter-health")
    x.add_argument("--name", required=True)

    x = s.add_parser("run-checks")
    x.add_argument("--workspace", default=".")
    x.add_argument("--preset", default="python")

    return p


def main(argv=None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    try:
        if a.cmd == "adapters":
            caps = get_registry().list_capabilities()
            out = {k: v.__dict__ for k, v in caps.items()}
        elif a.cmd == "adapter-health":
            adapter = get_registry().get(a.name)
            if hasattr(adapter, "health"):
                out = adapter.health()
            else:
                out = {"adapter": a.name, "healthy": True, "capabilities": adapter.capabilities().__dict__}
        elif a.cmd == "run-checks":
            out = GateRunner(a.workspace).run_preset(a.preset)
        else:
            e = Maestro(a.db)
            if a.cmd == "start":
                out = e.start(
                    a.project_id,
                    a.title,
                    a.objective,
                    a.baseline,
                    actor=a.actor,
                    require_verified_checks=a.require_verified,
                )
            elif a.cmd == "coding-start":
                out = coding_start(
                    e,
                    a.project_id,
                    a.title,
                    a.objective,
                    workspace=a.workspace,
                    risk=a.risk,
                    actor=a.actor,
                )
            elif a.cmd == "coding-seed-work":
                out = coding_seed_work(e, a.wid, a.revision, actor=a.actor)
            elif a.cmd == "show":
                out = e.get(a.wid)
            elif a.cmd == "list":
                out = e.list(a.project)
            elif a.cmd == "ground":
                out = e.ground(a.wid, a.revision, packet(a.packet), actor=a.actor)
            elif a.cmd == "begin-momentum":
                out = e.begin_momentum(a.wid, a.revision, actor=a.actor)
            elif a.cmd == "deliver":
                out = e.deliver(a.wid, a.revision, packet(a.packet), actor=a.actor)
            elif a.cmd == "submit-mastery":
                out = e.submit_mastery(a.wid, a.revision, actor=a.actor)
            elif a.cmd == "review":
                out = e.review(
                    a.wid,
                    a.revision,
                    a.verdict,
                    json.loads(a.findings),
                    json.loads(a.evidence),
                    actor=a.actor,
                    candidate_ref=a.candidate_ref,
                    require_verified=a.require_verified,
                )
            elif a.cmd == "learn":
                out = e.learn(a.wid, a.revision, packet(a.packet), actor=a.actor)
            elif a.cmd == "unblock":
                out = e.unblock(a.wid, a.revision, actor=a.actor)
            elif a.cmd == "cancel":
                out = e.cancel(a.wid, a.revision, a.reason, actor=a.actor)
            elif a.cmd == "add-work":
                out = e.add_work_item(
                    a.wid,
                    a.revision,
                    a.title,
                    a.outcome,
                    a.role,
                    json.loads(a.acceptance),
                    json.loads(a.dependencies),
                    actor=a.actor,
                )
            elif a.cmd == "start-work":
                out = e.change_work_item(
                    a.wid, a.item, a.revision, "IN_PROGRESS", actor=a.actor
                )
            elif a.cmd == "complete-work":
                out = e.change_work_item(
                    a.wid,
                    a.item,
                    a.revision,
                    "COMPLETED",
                    json.loads(a.evidence),
                    actor=a.actor,
                )
            elif a.cmd == "work-items":
                out = e.work_items(a.wid)
            elif a.cmd == "assign":
                out = {
                    "assignment_id": e.assign(
                        a.wid, a.role, a.capability, packet(a.packet), actor=a.actor
                    )
                }
            elif a.cmd == "assignment":
                out = e.assignment_transition(
                    a.aid,
                    a.status,
                    packet(a.result) if a.result else None,
                    actor=a.actor,
                )
            elif a.cmd == "assignments":
                out = e.assignments(a.wid)
            elif a.cmd == "events":
                out = e.events(a.wid)

        print(json.dumps(out, indent=2, default=lambda o: o.__dict__))
        return 0
    except (WorkflowError, AdapterError, ValueError, OSError) as ex:
        print("maestro: " + str(ex), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
