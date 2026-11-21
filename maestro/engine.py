"""Persistent, project-agnostic Maestro workflow engine."""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

STAGES = ("GROUNDING", "MOMENTUM", "MASTERY", "REPETITION")
ROLES = (
    "ORCHESTRATOR",
    "ARCHITECT",
    "RESEARCHER",
    "BUILDER",
    "INDEPENDENT_REVIEWER",
    "DOMAIN_SPECIALIST",
)
VERDICTS = ("PASS", "FAIL", "BLOCKED", "CONDITIONAL")
EVIDENCE_CLASSES = (
    "VERIFIED",
    "OBSERVED",
    "INFERRED",
    "ASSUMED",
    "PLANNED",
    "BLOCKED",
    "SUPERSEDED",
)

ROLE_STAGE_POLICY = {
    "ARCHITECT": {"GROUNDING", "MOMENTUM"},
    "RESEARCHER": {"GROUNDING", "MOMENTUM", "MASTERY"},
    "BUILDER": {"MOMENTUM"},
    "INDEPENDENT_REVIEWER": {"MASTERY"},
    "DOMAIN_SPECIALIST": set(STAGES),
    "ORCHESTRATOR": set(STAGES),
}


class WorkflowError(Exception):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _dump(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _require_non_empty_str(value, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(f"{field} must be a non-empty string")
    return value.strip()


def _require_str_list(value, field: str, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise WorkflowError(f"{field} must be a list")
    if not allow_empty and not value:
        raise WorkflowError(f"{field} must not be empty")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise WorkflowError(f"{field} items must be non-empty strings")
    return value


class Maestro:
    """One durable state machine for any number of independent project flows."""

    def __init__(self, database=".maestro/state.sqlite3"):
        self.database = str(database)
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            cur = db.execute("PRAGMA journal_mode=WAL")
            cur.close()
            db.executescript(
                """
            CREATE TABLE IF NOT EXISTS workflows(
              id TEXT PRIMARY KEY,
              project_id TEXT NOT NULL,
              title TEXT NOT NULL,
              objective TEXT NOT NULL,
              stage TEXT NOT NULL CHECK(stage IN ('GROUNDING','MOMENTUM','MASTERY','REPETITION')),
              status TEXT NOT NULL CHECK(status IN ('ACTIVE','BLOCKED','COMPLETED','CANCELLED')),
              revision INTEGER NOT NULL DEFAULT 0,
              cycle INTEGER NOT NULL DEFAULT 1,
              progress INTEGER NOT NULL DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
              baseline_ref TEXT,
              grounding TEXT NOT NULL DEFAULT '{}',
              momentum TEXT NOT NULL DEFAULT '{}',
              mastery TEXT NOT NULL DEFAULT '{}',
              repetition TEXT NOT NULL DEFAULT '{}',
              grounding_cycle INTEGER NOT NULL DEFAULT 0,
              momentum_cycle INTEGER NOT NULL DEFAULT 0,
              mastery_cycle INTEGER NOT NULL DEFAULT 0,
              builder_actor TEXT,
              candidate_submitted INTEGER NOT NULL DEFAULT 0,
              fail_count INTEGER NOT NULL DEFAULT 0,
              require_verified_checks INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events(
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              workflow_id TEXT NOT NULL REFERENCES workflows(id),
              revision INTEGER NOT NULL,
              event_type TEXT NOT NULL,
              from_stage TEXT,
              to_stage TEXT,
              actor TEXT NOT NULL,
              payload TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
              BEGIN SELECT RAISE(ABORT,'event history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
              BEGIN SELECT RAISE(ABORT,'event history is append-only'); END;
            CREATE TABLE IF NOT EXISTS work_items(
              id TEXT PRIMARY KEY,
              workflow_id TEXT NOT NULL REFERENCES workflows(id),
              stage TEXT NOT NULL,
              title TEXT NOT NULL,
              outcome TEXT NOT NULL,
              owner_role TEXT NOT NULL,
              status TEXT NOT NULL,
              dependencies TEXT NOT NULL,
              acceptance TEXT NOT NULL,
              evidence TEXT NOT NULL DEFAULT '[]',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assignments(
              id TEXT PRIMARY KEY,
              workflow_id TEXT NOT NULL REFERENCES workflows(id),
              stage TEXT NOT NULL,
              role TEXT NOT NULL,
              capability TEXT NOT NULL,
              status TEXT NOT NULL,
              packet TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            """
            )
            cols = {r[1] for r in db.execute("PRAGMA table_info(workflows)")}
            migrations = {
                "cycle": "ALTER TABLE workflows ADD COLUMN cycle INTEGER NOT NULL DEFAULT 1",
                "grounding_cycle": "ALTER TABLE workflows ADD COLUMN grounding_cycle INTEGER NOT NULL DEFAULT 0",
                "momentum_cycle": "ALTER TABLE workflows ADD COLUMN momentum_cycle INTEGER NOT NULL DEFAULT 0",
                "mastery_cycle": "ALTER TABLE workflows ADD COLUMN mastery_cycle INTEGER NOT NULL DEFAULT 0",
                "builder_actor": "ALTER TABLE workflows ADD COLUMN builder_actor TEXT",
                "candidate_submitted": "ALTER TABLE workflows ADD COLUMN candidate_submitted INTEGER NOT NULL DEFAULT 0",
                "fail_count": "ALTER TABLE workflows ADD COLUMN fail_count INTEGER NOT NULL DEFAULT 0",
                "require_verified_checks": "ALTER TABLE workflows ADD COLUMN require_verified_checks INTEGER NOT NULL DEFAULT 0",
            }
            for col, ddl in migrations.items():
                if col not in cols:
                    db.execute(ddl)

    @contextmanager
    def _db(self, readonly: bool = False):
        db = sqlite3.connect(self.database, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=15000")
        try:
            yield db
            if not readonly and db.in_transaction:
                db.commit()
        except Exception:
            if db.in_transaction:
                db.rollback()
            raise
        finally:
            db.close()

    def _event(self, db, wid, rev, kind, old, new, actor, payload):
        db.execute(
            "INSERT INTO events(workflow_id,revision,event_type,from_stage,to_stage,actor,payload,created_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (wid, rev, kind, old, new, actor, _dump(payload), _now()),
        )

    def _snapshot(self, r) -> dict:
        return {
            "id": r["id"],
            "project_id": r["project_id"],
            "title": r["title"],
            "objective": r["objective"],
            "stage": r["stage"],
            "status": r["status"],
            "revision": r["revision"],
            "cycle": r["cycle"],
            "progress": r["progress"],
            "baseline_ref": r["baseline_ref"],
            "packets": {
                k: json.loads(r[k])
                for k in ("grounding", "momentum", "mastery", "repetition")
            },
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }

    def _stage_clear_tx(self, db, wid: str, stage: str) -> None:
        rows = db.execute(
            "SELECT title,status FROM work_items WHERE workflow_id=? AND stage=? ORDER BY created_at ASC, id ASC",
            (wid, stage),
        ).fetchall()
        pending = [
            f"{r['title']} ({r['status']})" for r in rows if r["status"] != "COMPLETED"
        ]
        if pending:
            raise WorkflowError(
                f"incomplete {stage} work items: " + "; ".join(pending)
            )

    def _fetch_for_write(self, db, wid: str, rev: int, allowed_statuses=("ACTIVE",)):
        r = db.execute("SELECT * FROM workflows WHERE id=?", (wid,)).fetchone()
        if not r:
            raise WorkflowError("unknown workflow: " + wid)
        if r["revision"] != rev:
            raise WorkflowError(
                f"stale revision: expected {rev}, current {r['revision']}"
            )
        if r["status"] not in allowed_statuses:
            raise WorkflowError("workflow is " + r["status"])
        return r

    def _update_tx(
        self,
        db,
        r,
        rev: int,
        actor: str,
        kind: str,
        payload: dict,
        updates: dict,
    ) -> dict:
        old_stage = r["stage"]
        new_stage = updates.get("stage", old_stage)
        next_rev = rev + 1
        updates = dict(updates)
        updates["updated_at"] = _now()
        updates["revision"] = next_rev
        sql = (
            "UPDATE workflows SET "
            + ",".join(f"{k}=?" for k in updates)
            + " WHERE id=? AND revision=?"
        )
        cur = db.execute(sql, tuple(updates.values()) + (r["id"], rev))
        if cur.rowcount != 1:
            raise WorkflowError("concurrent update; reload workflow")
        self._event(db, r["id"], next_rev, kind, old_stage, new_stage, actor, payload)
        updated = db.execute(
            "SELECT * FROM workflows WHERE id=?", (r["id"],)
        ).fetchone()
        return self._snapshot(updated)

    def get(self, wid: str) -> dict:
        with self._db(readonly=True) as db:
            r = db.execute("SELECT * FROM workflows WHERE id=?", (wid,)).fetchone()
        if not r:
            raise WorkflowError("unknown workflow: " + wid)
        return self._snapshot(r)

    def list(self, project_id: str | None = None) -> list[dict]:
        with self._db(readonly=True) as db:
            rows = db.execute(
                "SELECT * FROM workflows"
                + (" WHERE project_id=?" if project_id else "")
                + " ORDER BY updated_at DESC, id ASC",
                (project_id,) if project_id else (),
            ).fetchall()
        return [self._snapshot(r) for r in rows]

    def start(
        self,
        project_id: str,
        title: str,
        objective: str,
        baseline_ref: str | None = None,
        actor: str = "human",
        require_verified_checks: bool = False,
    ) -> dict:
        project_id = _require_non_empty_str(project_id, "project_id")
        title = _require_non_empty_str(title, "title")
        objective = _require_non_empty_str(objective, "objective")
        actor = _require_non_empty_str(actor, "actor")
        wid, stamp = str(uuid.uuid4()), _now()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "INSERT INTO workflows(id,project_id,title,objective,stage,status,baseline_ref,require_verified_checks,created_at,updated_at) "
                "VALUES(?,?,?,?,'GROUNDING','ACTIVE',?,?,?,?)",
                (
                    wid,
                    project_id,
                    title,
                    objective,
                    baseline_ref,
                    1 if require_verified_checks else 0,
                    stamp,
                    stamp,
                ),
            )
            self._event(
                db,
                wid,
                0,
                "WORKFLOW_STARTED",
                None,
                "GROUNDING",
                actor,
                {"objective": objective},
            )
            row = db.execute("SELECT * FROM workflows WHERE id=?", (wid,)).fetchone()
            return self._snapshot(row)

    def ground(self, wid: str, rev: int, p: dict, actor: str = "orchestrator") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        if not isinstance(p, dict):
            raise WorkflowError("grounding packet must be an object")
        keys = (
            "purpose",
            "sources",
            "constraints",
            "dependencies",
            "risks",
            "acceptance",
            "next_increment",
        )
        missing = [k for k in keys if k not in p or p[k] is None]
        if missing:
            raise WorkflowError("grounding packet missing: " + ", ".join(missing))
        _require_non_empty_str(p["purpose"], "purpose")
        _require_non_empty_str(p["next_increment"], "next_increment")
        _require_str_list(p["sources"], "sources", allow_empty=False)
        _require_str_list(p["acceptance"], "acceptance", allow_empty=False)
        for k in ("constraints", "dependencies", "risks"):
            _require_str_list(p[k], k, allow_empty=True)

        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] != "GROUNDING":
                raise WorkflowError("ground only in GROUNDING")
            self._stage_clear_tx(db, wid, "GROUNDING")
            updates = {
                "grounding": _dump(p),
                "grounding_cycle": r["cycle"],
            }
            if p.get("baseline_ref") is not None:
                updates["baseline_ref"] = p["baseline_ref"]
            return self._update_tx(
                db, r, rev, actor, "GROUNDING_ACCEPTED", p, updates
            )

    def begin_momentum(self, wid: str, rev: int, actor: str = "orchestrator") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] != "GROUNDING":
                raise WorkflowError("Momentum requires Grounding")
            grounding = json.loads(r["grounding"])
            if not grounding or r["grounding_cycle"] != r["cycle"]:
                raise WorkflowError("Momentum requires current-cycle Grounding")
            self._stage_clear_tx(db, wid, "GROUNDING")
            return self._update_tx(
                db,
                r,
                rev,
                actor,
                "MOMENTUM_BEGAN",
                {"increment": grounding["next_increment"]},
                {"stage": "MOMENTUM"},
            )

    def deliver(self, wid: str, rev: int, p: dict, actor: str = "builder") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        if not isinstance(p, dict):
            raise WorkflowError("Momentum packet must be an object")
        for k in ("candidate_ref", "outcome", "changed_artifacts", "checks", "risks"):
            if k not in p or p[k] is None:
                raise WorkflowError("Momentum packet missing: " + k)
        _require_non_empty_str(p["candidate_ref"], "candidate_ref")
        _require_non_empty_str(p["outcome"], "outcome")
        _require_str_list(p["changed_artifacts"], "changed_artifacts", allow_empty=True)
        _require_str_list(p["risks"], "risks", allow_empty=True)
        if not isinstance(p["checks"], list):
            raise WorkflowError("checks must be a list")
        for c in p["checks"]:
            if (
                not isinstance(c, dict)
                or not isinstance(c.get("name"), str)
                or not c["name"].strip()
                or c.get("outcome") not in ("passed", "failed", "skipped", "not_run")
            ):
                raise WorkflowError("each check needs a name and valid outcome")
            ev_class = c.get("evidence_class")
            if ev_class is not None and ev_class not in EVIDENCE_CLASSES:
                raise WorkflowError(f"invalid check evidence_class: {ev_class}")

        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] != "MOMENTUM":
                raise WorkflowError("deliver only in MOMENTUM")
            if r["candidate_submitted"]:
                raise WorkflowError("candidate already submitted to Mastery")
            return self._update_tx(
                db,
                r,
                rev,
                actor,
                "MOMENTUM_DELIVERED",
                p,
                {
                    "momentum": _dump(p),
                    "momentum_cycle": r["cycle"],
                    "builder_actor": actor,
                    "candidate_submitted": 0,
                },
            )

    def submit_mastery(self, wid: str, rev: int, actor: str = "orchestrator") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] != "MOMENTUM":
                raise WorkflowError("Mastery requires Momentum candidate")
            grounding = json.loads(r["grounding"])
            momentum = json.loads(r["momentum"])
            if (
                not grounding
                or r["grounding_cycle"] != r["cycle"]
                or not momentum
                or r["momentum_cycle"] != r["cycle"]
            ):
                raise WorkflowError("Mastery requires current-cycle Momentum candidate")
            self._stage_clear_tx(db, wid, "MOMENTUM")
            payload = {
                "candidate_ref": momentum["candidate_ref"],
                "acceptance": grounding["acceptance"],
                "fail_count": r["fail_count"],
                "requires_root_cause": r["fail_count"] >= 2,
            }
            return self._update_tx(
                db,
                r,
                rev,
                actor,
                "MASTERY_SUBMITTED",
                payload,
                {
                    "stage": "MASTERY",
                    "mastery": _dump(payload),
                    "mastery_cycle": r["cycle"],
                    "candidate_submitted": 1,
                },
            )

    def review(
        self,
        wid: str,
        rev: int,
        verdict: str,
        findings: list,
        evidence: list,
        actor: str = "independent_reviewer",
        candidate_ref: str | None = None,
        require_verified: bool | None = None,
    ) -> dict:
        actor = _require_non_empty_str(actor, "actor")
        v = verdict.upper()
        if v not in VERDICTS:
            raise WorkflowError("invalid Mastery verdict")
        if not isinstance(findings, list) or not isinstance(evidence, list):
            raise WorkflowError("findings/evidence must be lists")

        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] != "MASTERY":
                raise WorkflowError("review only in MASTERY")
            momentum = json.loads(r["momentum"])
            if (
                not momentum
                or r["momentum_cycle"] != r["cycle"]
                or not r["candidate_submitted"]
            ):
                raise WorkflowError("no submitted current-cycle candidate to review")
            self._stage_clear_tx(db, wid, "MASTERY")

            builder = r["builder_actor"]
            if builder and actor.lower() == builder.strip().lower():
                raise WorkflowError(
                    "reviewer independence violated: reviewer actor cannot equal builder"
                )

            submitted_ref = momentum["candidate_ref"]
            if candidate_ref is not None and candidate_ref != submitted_ref:
                raise WorkflowError(
                    f"candidate_ref mismatch: expected {submitted_ref}, got {candidate_ref}"
                )

            if v in ("PASS", "CONDITIONAL"):
                _require_str_list(evidence, "evidence", allow_empty=False)
            if v == "CONDITIONAL" and not findings:
                raise WorkflowError("CONDITIONAL requires tracked findings")
            if v == "PASS":
                checks = momentum.get("checks", [])
                required_checks = [c for c in checks if c.get("required", True)]
                if not required_checks:
                    raise WorkflowError("PASS requires at least one required check")
                bad = [
                    c.get("name", "unnamed")
                    for c in required_checks
                    if c.get("outcome") != "passed"
                ]
                if bad:
                    raise WorkflowError(
                        "required Momentum checks not passed: " + ", ".join(bad)
                    )
                enforce_verified = (
                    bool(r["require_verified_checks"])
                    if require_verified is None
                    else require_verified
                )
                for c in required_checks:
                    ev_cls = c.get("evidence_class")
                    if ev_cls is not None and ev_cls != "VERIFIED":
                        raise WorkflowError(
                            f"check '{c.get('name')}' has non-verified evidence class: {ev_cls}"
                        )
                    if enforce_verified:
                        if (
                            ev_cls != "VERIFIED"
                            or c.get("exit_code") != 0
                            or not isinstance(c.get("log_hash"), str)
                            or not c.get("log_hash").strip()
                        ):
                            raise WorkflowError(
                                f"check '{c.get('name')}' lacks GateRunner VERIFIED proof (log_hash + exit_code=0)"
                            )

            p = {
                "verdict": v,
                "findings": findings,
                "evidence": evidence,
                "candidate_ref": submitted_ref,
                "reviewer_actor": actor,
            }
            if v == "FAIL":
                if not findings:
                    raise WorkflowError("FAIL requires findings")
                new_fail_count = r["fail_count"] + 1
                p["fail_count"] = new_fail_count
                p["requires_root_cause"] = new_fail_count >= 2
                return self._update_tx(
                    db,
                    r,
                    rev,
                    actor,
                    "MASTERY_FAILED",
                    p,
                    {
                        "stage": "MOMENTUM",
                        "mastery": _dump(p),
                        "mastery_cycle": r["cycle"],
                        "candidate_submitted": 0,
                        "fail_count": new_fail_count,
                    },
                )
            if v == "BLOCKED":
                if not findings:
                    raise WorkflowError("BLOCKED requires blocker")
                return self._update_tx(
                    db,
                    r,
                    rev,
                    actor,
                    "MASTERY_BLOCKED",
                    p,
                    {
                        "status": "BLOCKED",
                        "mastery": _dump(p),
                        "mastery_cycle": r["cycle"],
                    },
                )
            return self._update_tx(
                db,
                r,
                rev,
                actor,
                "MASTERY_REVIEWED",
                p,
                {
                    "stage": "REPETITION",
                    "mastery": _dump(p),
                    "mastery_cycle": r["cycle"],
                },
            )

    def learn(self, wid: str, rev: int, p: dict, actor: str = "orchestrator") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        if not isinstance(p, dict):
            raise WorkflowError("Repetition packet must be an object")
        for k in ("expected_vs_actual", "lessons", "state_updates", "next_decision", "evidence"):
            if k not in p or p[k] is None:
                raise WorkflowError("Repetition packet missing: " + k)
        _require_non_empty_str(p["expected_vs_actual"], "expected_vs_actual")
        _require_non_empty_str(p["next_decision"], "next_decision")
        _require_str_list(p["lessons"], "lessons", allow_empty=True)
        _require_str_list(p["state_updates"], "state_updates", allow_empty=True)
        _require_str_list(p["evidence"], "evidence", allow_empty=False)

        complete = p.get("objective_complete", False)
        if not isinstance(complete, bool):
            raise WorkflowError("objective_complete must be boolean")

        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] != "REPETITION":
                raise WorkflowError("learn only in REPETITION")
            mastery = json.loads(r["mastery"])
            if r["mastery_cycle"] != r["cycle"] or mastery.get("verdict") not in (
                "PASS",
                "CONDITIONAL",
            ):
                raise WorkflowError("Repetition requires accepted current-cycle Mastery verdict")
            self._stage_clear_tx(db, wid, "REPETITION")

            if "progress" in p:
                progress = p["progress"]
                if (
                    isinstance(progress, bool)
                    or not isinstance(progress, int)
                    or not 0 <= progress <= 100
                ):
                    raise WorkflowError("invalid completion/progress")
                if progress < r["progress"]:
                    raise WorkflowError("objective progress cannot move backwards")
                if complete and progress != 100:
                    raise WorkflowError("completed objective progress must be 100")
            else:
                progress = 100 if complete else r["progress"]

            if complete:
                return self._update_tx(
                    db,
                    r,
                    rev,
                    actor,
                    "WORKFLOW_COMPLETED",
                    p,
                    {
                        "stage": "REPETITION",
                        "status": "COMPLETED",
                        "progress": 100,
                        "cycle": r["cycle"],
                        "repetition": _dump(p),
                    },
                )
            return self._update_tx(
                db,
                r,
                rev,
                actor,
                "CYCLE_LEARNED",
                p,
                {
                    "stage": "GROUNDING",
                    "status": "ACTIVE",
                    "progress": progress,
                    "cycle": r["cycle"] + 1,
                    "repetition": _dump(p),
                    "grounding": "{}",
                    "momentum": "{}",
                    "mastery": "{}",
                    "grounding_cycle": 0,
                    "momentum_cycle": 0,
                    "mastery_cycle": 0,
                    "builder_actor": None,
                    "candidate_submitted": 0,
                    "fail_count": 0,
                },
            )

    def unblock(self, wid: str, rev: int, actor: str = "orchestrator") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev, allowed_statuses=("BLOCKED",))
            return self._update_tx(
                db, r, rev, actor, "WORKFLOW_UNBLOCKED", {}, {"status": "ACTIVE"}
            )

    def cancel(self, wid: str, rev: int, reason: str, actor: str = "human") -> dict:
        actor = _require_non_empty_str(actor, "actor")
        reason = _require_non_empty_str(reason, "cancellation reason")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(
                db, wid, rev, allowed_statuses=("ACTIVE", "BLOCKED")
            )
            return self._update_tx(
                db,
                r,
                rev,
                actor,
                "WORKFLOW_CANCELLED",
                {"reason": reason},
                {"status": "CANCELLED"},
            )

    def add_work_item(
        self,
        wid: str,
        rev: int,
        title: str,
        outcome: str,
        owner_role: str,
        acceptance: list[str],
        dependencies: list[str] | None = None,
        actor: str = "orchestrator",
    ) -> dict:
        actor = _require_non_empty_str(actor, "actor")
        role = _require_non_empty_str(owner_role, "owner_role").upper()
        title = _require_non_empty_str(title, "title")
        outcome = _require_non_empty_str(outcome, "outcome")
        deps = dependencies or []
        _require_str_list(acceptance, "acceptance", allow_empty=False)
        _require_str_list(deps, "dependencies", allow_empty=True)
        if role not in ROLES:
            raise WorkflowError("invalid work item role: " + role)

        iid, stamp = str(uuid.uuid4()), _now()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            if r["stage"] not in ROLE_STAGE_POLICY[role]:
                raise WorkflowError(f"{role} not allowed in {r['stage']}")
            known = {
                row[0]
                for row in db.execute(
                    "SELECT id FROM work_items WHERE workflow_id=?", (wid,)
                )
            }
            if set(deps) - known:
                raise WorkflowError("unknown dependency")
            db.execute(
                "INSERT INTO work_items VALUES(?,?,?,?,?,?,'READY',?,?, '[]',?,?)",
                (
                    iid,
                    wid,
                    r["stage"],
                    title,
                    outcome,
                    role,
                    _dump(deps),
                    _dump(acceptance),
                    stamp,
                    stamp,
                ),
            )
            self._event(
                db,
                wid,
                r["revision"],
                "WORK_ITEM_CREATED",
                r["stage"],
                r["stage"],
                actor,
                {"id": iid, "title": title},
            )
        return {"id": iid, "workflow_revision": r["revision"], "stage": r["stage"]}

    def change_work_item(
        self,
        wid: str,
        iid: str,
        rev: int,
        status: str,
        evidence: list[str] | None = None,
        actor: str = "human",
    ) -> dict:
        actor = _require_non_empty_str(actor, "actor")
        evidence = evidence or []
        stamp = _now()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = self._fetch_for_write(db, wid, rev)
            item = db.execute(
                "SELECT * FROM work_items WHERE id=? AND workflow_id=?", (iid, wid)
            ).fetchone()
            if not item or item["stage"] != r["stage"]:
                raise WorkflowError("unknown or stale work item")
            allowed = {"READY": "IN_PROGRESS", "IN_PROGRESS": "COMPLETED"}
            if allowed.get(item["status"]) != status:
                raise WorkflowError("invalid work-item transition")
            if status == "IN_PROGRESS":
                for dep in json.loads(item["dependencies"]):
                    dep_row = db.execute(
                        "SELECT status FROM work_items WHERE id=? AND workflow_id=?",
                        (dep, wid),
                    ).fetchone()
                    if not dep_row or dep_row["status"] != "COMPLETED":
                        raise WorkflowError("work-item dependency incomplete")
            if status == "COMPLETED":
                _require_str_list(evidence, "evidence", allow_empty=False)
            db.execute(
                "UPDATE work_items SET status=?,evidence=?,updated_at=? WHERE id=?",
                (status, _dump(evidence), stamp, iid),
            )
            self._event(
                db,
                wid,
                r["revision"],
                "WORK_ITEM_" + status,
                r["stage"],
                r["stage"],
                actor,
                {"id": iid, "evidence": evidence},
            )
        return {"id": iid, "status": status, "workflow_revision": r["revision"]}

    def work_items(self, wid: str) -> list[dict]:
        with self._db(readonly=True) as db:
            rows = db.execute(
                "SELECT * FROM work_items WHERE workflow_id=? ORDER BY created_at ASC, id ASC",
                (wid,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "stage": r["stage"],
                "title": r["title"],
                "outcome": r["outcome"],
                "owner_role": r["owner_role"],
                "status": r["status"],
                "dependencies": json.loads(r["dependencies"]),
                "acceptance": json.loads(r["acceptance"]),
                "evidence": json.loads(r["evidence"]),
            }
            for r in rows
        ]

    def assign(
        self,
        wid: str,
        role: str,
        capability: str,
        packet: dict,
        actor: str = "orchestrator",
    ) -> str:
        actor = _require_non_empty_str(actor, "actor")
        role = _require_non_empty_str(role, "role").upper()
        capability = _require_non_empty_str(capability, "capability")
        if role not in ROLES or role == "ORCHESTRATOR":
            raise WorkflowError("role not allowed for specialist assignment")
        aid, stamp = str(uuid.uuid4()), _now()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            r = db.execute("SELECT * FROM workflows WHERE id=?", (wid,)).fetchone()
            if not r:
                raise WorkflowError("unknown workflow: " + wid)
            if r["status"] != "ACTIVE" or r["stage"] not in ROLE_STAGE_POLICY[role]:
                raise WorkflowError("role not allowed in current stage")
            dispatch = {
                "workflow_id": wid,
                "project_id": r["project_id"],
                "stage": r["stage"],
                "cycle": r["cycle"],
                "workflow_revision": r["revision"],
                "role": role,
                "capability": capability,
                "expected_output": packet,
                "permission_boundary": "least_privilege",
            }
            db.execute(
                "INSERT INTO assignments VALUES(?,?,?,?,?,'PROPOSED',?,?,?)",
                (aid, wid, r["stage"], role, capability, _dump(dispatch), stamp, stamp),
            )
            self._event(
                db,
                wid,
                r["revision"],
                "ASSIGNMENT_PROPOSED",
                r["stage"],
                r["stage"],
                actor,
                {"id": aid, "role": role},
            )
        return aid

    def assignment_transition(
        self,
        aid: str,
        status: str,
        result: dict | None = None,
        actor: str = "orchestrator",
    ) -> dict:
        actor = _require_non_empty_str(actor, "actor")
        status = _require_non_empty_str(status, "status").upper()
        transitions = {
            "PROPOSED": {"ACCEPTED", "CANCELLED"},
            "ACCEPTED": {"RUNNING", "CANCELLED"},
            "RUNNING": {"RETURNED", "CANCELLED"},
        }
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            a = db.execute("SELECT * FROM assignments WHERE id=?", (aid,)).fetchone()
            if not a or status not in transitions.get(a["status"], set()):
                raise WorkflowError("invalid assignment transition")
            w = db.execute(
                "SELECT * FROM workflows WHERE id=?", (a["workflow_id"],)
            ).fetchone()
            p = json.loads(a["packet"])
            if (
                not w
                or w["stage"] != a["stage"]
                or w["cycle"] != p.get("cycle", w["cycle"])
                or w["status"] != "ACTIVE"
            ):
                raise WorkflowError("stale assignment")
            if status == "RETURNED":
                if not isinstance(result, dict):
                    raise WorkflowError("return requires result object")
                _require_non_empty_str(result.get("summary"), "result.summary")
                _require_str_list(
                    result.get("evidence"), "result.evidence", allow_empty=False
                )
                p["result"] = result
            stamp = _now()
            db.execute(
                "UPDATE assignments SET status=?,packet=?,updated_at=? WHERE id=?",
                (status, _dump(p), stamp, aid),
            )
            self._event(
                db,
                a["workflow_id"],
                w["revision"],
                "ASSIGNMENT_" + status,
                a["stage"],
                a["stage"],
                actor,
                {"id": aid},
            )
        return {"id": aid, "status": status, "packet": p}

    def assignments(self, wid: str) -> list[dict]:
        with self._db(readonly=True) as db:
            rows = db.execute(
                "SELECT * FROM assignments WHERE workflow_id=? ORDER BY created_at ASC, id ASC",
                (wid,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "stage": r["stage"],
                "role": r["role"],
                "capability": r["capability"],
                "status": r["status"],
                "packet": json.loads(r["packet"]),
            }
            for r in rows
        ]

    def events(self, wid: str) -> list[dict]:
        with self._db(readonly=True) as db:
            rows = db.execute(
                "SELECT * FROM events WHERE workflow_id=? ORDER BY seq ASC", (wid,)
            ).fetchall()
        return [
            {
                "seq": r["seq"],
                "revision": r["revision"],
                "type": r["event_type"],
                "from": r["from_stage"],
                "to": r["to_stage"],
                "actor": r["actor"],
                "payload": json.loads(r["payload"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]
