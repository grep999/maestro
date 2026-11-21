"""Coding workflow helpers: git identity, safe worktrees, packet builders, and seeding."""
from __future__ import annotations

import subprocess
from pathlib import Path

from .engine import Maestro, WorkflowError

VALID_RISKS = ("R0", "R1", "R2", "R3")


def _run_git(args: list[str], workspace: str | Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=Path(workspace).resolve(),
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
        shell=False,
    )


def git_head_sha(workspace: str | Path = ".") -> str | None:
    proc = _run_git(["rev-parse", "HEAD"], workspace)
    sha = proc.stdout.strip()
    return sha if proc.returncode == 0 and len(sha) == 40 else None


def git_branch(workspace: str | Path = ".") -> str | None:
    proc = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], workspace)
    branch = proc.stdout.strip()
    return branch if proc.returncode == 0 and branch else None


def worktree_add(
    repo: str | Path, path: str | Path, branch: str, base_ref: str = "HEAD"
) -> Path:
    if not branch.strip() or branch.startswith("-"):
        raise WorkflowError("invalid branch name")
    target = Path(path).resolve()
    proc = _run_git(["worktree", "add", "-b", branch, str(target), base_ref], repo)
    if proc.returncode != 0:
        raise WorkflowError(f"git worktree add failed: {proc.stderr.strip()}")
    return target


def worktree_remove(repo: str | Path, path: str | Path) -> None:
    proc = _run_git(["worktree", "remove", str(Path(path).resolve())], repo)
    if proc.returncode != 0:
        raise WorkflowError(f"git worktree remove failed: {proc.stderr.strip()}")


def build_coding_grounding_packet(
    title: str,
    objective: str,
    workspace: str | Path = ".",
    risk: str = "R1",
    baseline_ref: str | None = None,
) -> dict:
    risk = risk.upper()
    if risk not in VALID_RISKS:
        raise WorkflowError(f"invalid risk tier '{risk}'; expected one of {VALID_RISKS}")
    ws = Path(workspace).resolve()
    sha = git_head_sha(ws)
    branch = git_branch(ws)
    ref = baseline_ref or (f"git:{branch}@{sha}" if sha and branch else f"path:{ws}")
    sources = [ref]
    if sha:
        sources.append(f"sha:{sha}")
    acceptance = [
        objective.strip(),
        "deterministic verification checks pass with VERIFIED evidence",
    ]
    if risk in ("R1", "R2", "R3"):
        acceptance.append("independent reviewer examines exact candidate_ref")
    if risk in ("R2", "R3"):
        acceptance.append("explicit human approval recorded before external merge/deploy")
    return {
        "purpose": objective.strip(),
        "sources": sources,
        "constraints": [
            "work in isolated branch or worktree",
            "no secrets in commits or logs",
            "no unapproved merge, publish, or deploy",
        ],
        "dependencies": [],
        "risks": [f"risk tier {risk}"],
        "acceptance": acceptance,
        "next_increment": f"Implement {title.strip()} with verification checks",
        "baseline_ref": sha or ref,
    }


def coding_start(
    engine: Maestro,
    project_id: str,
    title: str,
    objective: str,
    workspace: str | Path = ".",
    risk: str = "R1",
    actor: str = "human",
) -> dict:
    pkt = build_coding_grounding_packet(title, objective, workspace=workspace, risk=risk)
    w = engine.start(
        project_id=project_id,
        title=title,
        objective=objective,
        baseline_ref=pkt["baseline_ref"],
        actor=actor,
        require_verified_checks=(risk.upper() in ("R1", "R2", "R3")),
    )
    return engine.ground(w["id"], w["revision"], pkt, actor=actor)


def coding_seed_work(
    engine: Maestro,
    wid: str,
    rev: int,
    actor: str = "orchestrator",
) -> list[dict]:
    w = engine.get(wid)
    if w["stage"] == "GROUNDING":
        r1 = engine.add_work_item(
            wid,
            rev,
            "Inspect repository & baseline",
            "Verify canonical sources and baseline SHA",
            "RESEARCHER",
            ["baseline SHA and constraints confirmed"],
            actor=actor,
        )
        r2 = engine.add_work_item(
            wid,
            r1["workflow_revision"],
            "Design increment & acceptance",
            "Define coherent increment boundary and checks",
            "ARCHITECT",
            ["acceptance criteria and interface boundaries explicit"],
            dependencies=[r1["id"]],
            actor=actor,
        )
        return [r1, r2]
    if w["stage"] == "MOMENTUM":
        i1 = engine.add_work_item(
            wid,
            rev,
            "Research implementation context",
            "Confirm target files and test harness",
            "RESEARCHER",
            ["target files and dependencies verified"],
            actor=actor,
        )
        i2 = engine.add_work_item(
            wid,
            i1["workflow_revision"],
            "Implement candidate increment",
            "Build code and unit tests in isolated worktree",
            "BUILDER",
            ["candidate committed on isolated branch"],
            dependencies=[i1["id"]],
            actor=actor,
        )
        i3 = engine.add_work_item(
            wid,
            i2["workflow_revision"],
            "Run deterministic gate checks",
            "Capture VERIFIED GateRunner output on candidate SHA",
            "DOMAIN_SPECIALIST",
            ["all required GateRunner checks passed with log_hash"],
            dependencies=[i2["id"]],
            actor=actor,
        )
        return [i1, i2, i3]
    raise WorkflowError(
        f"coding-seed-work supports GROUNDING or MOMENTUM, not {w['stage']}"
    )
