"""Persistent, project-agnostic Maestro workflow engine."""
from __future__ import annotations

import sys
from types import ModuleType

def _assemble() -> ModuleType:
    parts: list[str] = []
    i = 0
    while True:
        name = f"maestro._engine_src_{i}"
        try:
            mod = __import__(name, fromlist=["SRC"])
        except ImportError:
            break
        parts.append(mod.SRC)
        i += 1
    if not parts:
        raise ImportError("maestro engine source chunks missing")
    code = "".join(parts)
    mod = ModuleType(__name__)
    mod.__file__ = __file__
    exec(compile(code, __file__, "exec"), mod.__dict__)
    return mod

_m = _assemble()
# Public API
STAGES = _m.STAGES
ROLES = _m.ROLES
VERDICTS = _m.VERDICTS
EVIDENCE_CLASSES = _m.EVIDENCE_CLASSES
ROLE_STAGE_POLICY = _m.ROLE_STAGE_POLICY
WorkflowError = _m.WorkflowError
Maestro = _m.Maestro
# Re-export helpers used by tests/other modules if needed
_now = getattr(_m, "_now", None)
_dump = getattr(_m, "_dump", None)

# Populate this module fully so `from maestro.engine import *` and getattr work
sys.modules[__name__].__dict__.update(
    {k: v for k, v in _m.__dict__.items() if not k.startswith("__")}
)
