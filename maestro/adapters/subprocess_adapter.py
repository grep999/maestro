"""Built-in Echo and safe Subprocess agent adapters."""
from __future__ import annotations

import os
import signal
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .protocol import (
    AdapterCapability,
    AdapterError,
    AgentEvent,
    AgentResult,
    AssignmentPacket,
    EventKind,
    register_adapter,
)

SAFE_BASE_ENV_KEYS = ("PATH", "LANG", "LC_ALL", "TERM", "HOME", "USER", "TMPDIR", "TEMP", "TMP")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class EchoAdapter:
    """Deterministic in-process reference adapter for smoke tests and health probes."""

    def __init__(self, model_identity: str = "echo-v1"):
        self._model_identity = model_identity
        self._runs: dict[str, tuple[AssignmentPacket, list[AgentEvent], AgentResult]] = {}
        self._lock = threading.Lock()

    def capabilities(self) -> AdapterCapability:
        return AdapterCapability(
            name="echo",
            roles=("ARCHITECT", "RESEARCHER", "BUILDER", "INDEPENDENT_REVIEWER", "DOMAIN_SPECIALIST"),
            model_identity=self._model_identity,
            supports_streaming=True,
            supports_cancel=True,
            isolation="in_process",
        )

    def health(self) -> dict:
        return {"adapter": "echo", "healthy": True, "model_identity": self._model_identity}

    def start(self, packet: AssignmentPacket) -> str:
        run_id = packet.run_id or str(uuid.uuid4())
        events = [
            AgentEvent(EventKind.STARTED, f"echo started for {packet.role}", _now()),
            AgentEvent(EventKind.MESSAGE, packet.instructions, _now()),
            AgentEvent(EventKind.COMPLETED, "echo finished", _now()),
        ]
        res = AgentResult(
            run_id=run_id,
            status="completed",
            summary=f"echo processed {packet.capability} for {packet.role}",
            evidence=[f"echo:{run_id}"],
            model_identity=self._model_identity,
            exit_code=0,
        )
        with self._lock:
            self._runs[run_id] = (packet, events, res)
        return run_id

    def stream(self, run_id: str) -> Iterator[AgentEvent]:
        with self._lock:
            if run_id not in self._runs:
                raise AdapterError(f"unknown run_id: {run_id}")
            events = list(self._runs[run_id][1])
        return iter(events)

    def result(self, run_id: str) -> AgentResult:
        with self._lock:
            if run_id not in self._runs:
                raise AdapterError(f"unknown run_id: {run_id}")
            return self._runs[run_id][2]

    def cancel(self, run_id: str) -> None:
        with self._lock:
            if run_id not in self._runs:
                raise AdapterError(f"unknown run_id: {run_id}")
            pkt, events, _ = self._runs[run_id]
            events.append(AgentEvent(EventKind.CANCELLED, "echo cancelled", _now()))
            self._runs[run_id] = (
                pkt,
                events,
                AgentResult(
                    run_id=run_id,
                    status="cancelled",
                    summary="echo run cancelled",
                    model_identity=self._model_identity,
                    exit_code=-1,
                ),
            )


@dataclass
class _SubprocessRun:
    packet: AssignmentPacket
    proc: subprocess.Popen
    events: list[AgentEvent] = field(default_factory=list)
    cancelled: bool = False
    result: AgentResult | None = None


class SubprocessAdapter:
    """Runs an external CLI agent via Popen(shell=False) with scoped env and pgid cancel."""

    def __init__(
        self,
        name: str,
        command: list[str],
        model_identity: str,
        roles: tuple[str, ...] = ("BUILDER", "INDEPENDENT_REVIEWER"),
    ):
        if not command:
            raise AdapterError("command must be non-empty")
        self._name = name
        self._command = list(command)
        self._model_identity = model_identity
        self._roles = roles
        self._runs: dict[str, _SubprocessRun] = {}
        self._lock = threading.Lock()

    def capabilities(self) -> AdapterCapability:
        return AdapterCapability(
            name=self._name,
            roles=self._roles,
            model_identity=self._model_identity,
            supports_streaming=True,
            supports_cancel=True,
            isolation="subprocess",
        )

    def start(self, packet: AssignmentPacket) -> str:
        workspace = Path(packet.workspace).resolve()
        if not workspace.is_dir():
            raise AdapterError(f"workspace directory not found: {workspace}")
        run_id = packet.run_id or str(uuid.uuid4())
        env = {k: os.environ[k] for k in SAFE_BASE_ENV_KEYS if k in os.environ}
        for key in packet.env_allowlist:
            if key in os.environ:
                env[key] = os.environ[key]
        env["MAESTRO_RUN_ID"] = run_id
        env["MAESTRO_WORKFLOW_ID"] = packet.workflow_id
        env["MAESTRO_ROLE"] = packet.role

        try:
            proc = subprocess.Popen(
                self._command,
                cwd=workspace,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=False,
                start_new_session=True,
            )
        except OSError as exc:
            raise AdapterError(f"failed to start adapter '{self._name}': {exc}") from exc

        if proc.stdin is not None:
            try:
                proc.stdin.write(packet.instructions)
                proc.stdin.close()
            except OSError:
                pass

        run = _SubprocessRun(
            packet=packet,
            proc=proc,
            events=[AgentEvent(EventKind.STARTED, f"{self._name} started", _now())],
        )
        with self._lock:
            self._runs[run_id] = run
        return run_id

    def stream(self, run_id: str) -> Iterator[AgentEvent]:
        with self._lock:
            run = self._runs.get(run_id)
        if not run:
            raise AdapterError(f"unknown run_id: {run_id}")
        yield run.events[0]
        if run.proc.stdout is not None:
            for line in run.proc.stdout:
                ev = AgentEvent(EventKind.MESSAGE, line.rstrip("\n"), _now())
                with self._lock:
                    run.events.append(ev)
                yield ev

    def result(self, run_id: str) -> AgentResult:
        with self._lock:
            run = self._runs.get(run_id)
        if not run:
            raise AdapterError(f"unknown run_id: {run_id}")
        if run.result is not None:
            return run.result
        try:
            code = run.proc.wait(timeout=run.packet.timeout_seconds)
        except subprocess.TimeoutExpired:
            self.cancel(run_id)
            code = -1
        if run.proc.stdout is not None:
            leftover = run.proc.stdout.read()
            if leftover:
                for line in leftover.splitlines():
                    run.events.append(AgentEvent(EventKind.MESSAGE, line, _now()))
        status = "cancelled" if run.cancelled else ("completed" if code == 0 else "failed")
        res = AgentResult(
            run_id=run_id,
            status=status,
            summary=f"{self._name} exited with code {code}",
            evidence=[f"adapter:{self._name}:{run_id}:exit={code}"],
            model_identity=self._model_identity,
            exit_code=code,
        )
        with self._lock:
            run.result = res
        return res

    def cancel(self, run_id: str) -> None:
        with self._lock:
            run = self._runs.get(run_id)
        if not run:
            raise AdapterError(f"unknown run_id: {run_id}")
        run.cancelled = True
        proc = run.proc
        if proc.poll() is None:
            try:
                if os.name == "posix":
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                else:
                    proc.terminate()
            except OSError:
                pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    if os.name == "posix":
                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                    else:
                        proc.kill()
                except OSError:
                    pass
        with self._lock:
            run.events.append(AgentEvent(EventKind.CANCELLED, "process cancelled", _now()))


register_adapter("echo", EchoAdapter)
