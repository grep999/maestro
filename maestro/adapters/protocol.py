"""Agent adapter protocol and registry for Maestro."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterator, Protocol, runtime_checkable


class AdapterError(Exception):
    pass


class EventKind(str, Enum):
    STARTED = "started"
    TOOL_CALL = "tool_call"
    FILE_CHANGED = "file_changed"
    MESSAGE = "message"
    QUESTION = "question"
    CHECK = "check"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AdapterCapability:
    name: str
    roles: tuple[str, ...]
    model_identity: str
    supports_streaming: bool = True
    supports_cancel: bool = True
    isolation: str = "worktree"


@dataclass(frozen=True)
class AssignmentPacket:
    run_id: str
    workflow_id: str
    role: str
    capability: str
    workspace: str
    instructions: str
    expected_output: dict = field(default_factory=dict)
    timeout_seconds: int = 300
    env_allowlist: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentEvent:
    kind: EventKind
    message: str
    timestamp: str
    data: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    run_id: str
    status: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    candidate_sha: str | None = None
    changed_paths: list[str] = field(default_factory=list)
    checks: list[dict] = field(default_factory=list)
    model_identity: str = ""
    exit_code: int | None = None


@runtime_checkable
class AgentAdapter(Protocol):
    def capabilities(self) -> AdapterCapability: ...

    def start(self, packet: AssignmentPacket) -> str: ...

    def stream(self, run_id: str) -> Iterator[AgentEvent]: ...

    def result(self, run_id: str) -> AgentResult: ...

    def cancel(self, run_id: str) -> None: ...


class Registry:
    def __init__(self):
        self._factories: dict[str, Callable[[], AgentAdapter]] = {}

    def register(self, name: str, factory: Callable[[], AgentAdapter]) -> None:
        if not isinstance(name, str) or not name.strip():
            raise AdapterError("adapter name must be non-empty")
        self._factories[name.strip()] = factory

    def get(self, name: str) -> AgentAdapter:
        if name not in self._factories:
            raise AdapterError(f"unknown adapter: {name}")
        return self._factories[name]()

    def names(self) -> list[str]:
        return sorted(self._factories)

    def list_capabilities(self) -> dict[str, AdapterCapability]:
        return {name: self.get(name).capabilities() for name in self.names()}


_REGISTRY = Registry()


def get_registry() -> Registry:
    return _REGISTRY


def register_adapter(name: str, factory: Callable[[], AgentAdapter]) -> None:
    _REGISTRY.register(name, factory)
