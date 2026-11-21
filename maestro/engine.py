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
              actor TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS packets(
              id TEXT PRIMARY KEY,
              workflow_id TEXT NOT NULL REFERENCES workflows(id),
              stage TEXT NOT NULL,
              cycle INTEGER NOT NULL,
              kind TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
            )
