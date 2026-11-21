"""Agent adapter protocol for Maestro."""

from .protocol import (
    AdapterCapability,
    AdapterError,
    AgentAdapter,
    AgentEvent,
    AgentResult,
    AssignmentPacket,
    EventKind,
    Registry,
    get_registry,
    register_adapter,
)
from .subprocess_adapter import EchoAdapter, SubprocessAdapter

__all__ = [
    "AdapterCapability",
    "AdapterError",
    "AgentAdapter",
    "AgentEvent",
    "AgentResult",
    "AssignmentPacket",
    "EchoAdapter",
    "EventKind",
    "Registry",
    "SubprocessAdapter",
    "get_registry",
    "register_adapter",
]
