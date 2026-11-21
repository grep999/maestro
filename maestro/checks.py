"""Deterministic verification gate runner producing VERIFIED check evidence."""
from __future__ import annotations

import hashlib
import shlex
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: list[str] | str
    required: bool = True
    category: str = "test"
    timeout: int = 120


@dataclass(frozen=True)
class CheckResult:
    name: str
    outcome: str
    required: bool
    command: str
    exit_code: int
    log_hash: str
    evidence_class: str
    runner_identity: str
    ran_on_sha: str
    category: str
    duration_ms: int

    def to_dict(self) -> dict:
        return asdict(self)


def _python_presets() -> list[CheckSpec]:
    return [
        CheckSpec(
            name="compileall",
            command=[sys.executable, "-m", "compileall", "-q", "."],
            required=True,
            category="lint",
        ),
        CheckSpec(
            name="unit-tests",
            command=[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            required=True,
            category="test",
        ),
    ]


PRESET_FACTORIES = {
    "python": _python_presets,
    "smoke": lambda: [
        CheckSpec(
            name="compileall",
            command=[sys.executable, "-m", "compileall", "-q", "."],
            required=True,
            category="lint",
        )
    ],
}


def _git_sha(workspace: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        sha = proc.stdout.strip()
        if proc.returncode == 0 and len(sha) == 40:
            return sha
    except (OSError, subprocess.SubprocessError):
        pass
    return "0" * 40


class GateRunner:
    """Executes deterministic commands without shell=True and hashes full logs."""

    def __init__(
        self,
        workspace: str | Path = ".",
        runner_identity: str | None = None,
        timeout: int = 120,
    ):
        self.workspace = Path(workspace).resolve()
        if not self.workspace.is_dir():
            raise ValueError(f"workspace directory does not exist: {self.workspace}")
        self.runner_identity = runner_identity or f"gate-runner@{socket.gethostname()}"
        self.default_timeout = timeout

    def run_spec(self, spec: CheckSpec) -> CheckResult:
        cmd_list = (
            shlex.split(spec.command)
            if isinstance(spec.command, str)
            else list(spec.command)
        )
        if not cmd_list:
            raise ValueError(f"empty command for check '{spec.name}'")
        cmd_str = shlex.join(cmd_list)
        sha = _git_sha(self.workspace)
        started = time.monotonic()
        timeout = spec.timeout or self.default_timeout
        try:
            proc = subprocess.run(
                cmd_list,
                cwd=self.workspace,
                capture_output=True,
                timeout=timeout,
                check=False,
                shell=False,
            )
            raw_log = proc.stdout + proc.stderr
            exit_code = proc.returncode
            outcome = "passed" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            raw_log = (exc.stdout or b"") + (exc.stderr or b"") + b"\nTIMEOUT\n"
            exit_code = -1
            outcome = "failed"
        except OSError as exc:
            raw_log = f"OS error executing command: {exc}\n".encode("utf-8")
            exit_code = 127
            outcome = "failed"

        elapsed_ms = int((time.monotonic() - started) * 1000)
        log_hash = hashlib.sha256(raw_log).hexdigest()
        return CheckResult(
            name=spec.name,
            outcome=outcome,
            required=spec.required,
            command=cmd_str,
            exit_code=exit_code,
            log_hash=log_hash,
            evidence_class="VERIFIED",
            runner_identity=self.runner_identity,
            ran_on_sha=sha,
            category=spec.category,
            duration_ms=elapsed_ms,
        )

    def run(self, specs: list[CheckSpec]) -> list[dict]:
        return [self.run_spec(spec).to_dict() for spec in specs]

    def run_preset(self, preset: str) -> list[dict]:
        if preset not in PRESET_FACTORIES:
            raise ValueError(
                f"unknown preset '{preset}'; available: {', '.join(sorted(PRESET_FACTORIES))}"
            )
        return self.run(PRESET_FACTORIES[preset]())
