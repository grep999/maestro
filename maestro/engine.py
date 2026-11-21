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
