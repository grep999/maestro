"""Agent adapter protocol for Maestro.

Maestro is agent-agnostic: it never embeds a coding agent. Adapters translate
between Maestro assignment packets and concrete agent runtimes (Claude Code,
Codex, OpenCode, Gemini CLI, subprocess, MCP, ACP, etc.).

Design principles (PhD-grade agentic workflow engineering):

1. Capability discovery before dispatch — never assume tools exist.
2. Isolation by default — worktree / sandbox / scoped credentials.
3. Normalized event stream — tool calls, tokens, files, questions, completion.
4. Result is evidence, not trust — adapter returns structured result; gates verify.
5. Cancellation and timeout are first-class.
6. Identity of the running agent is recorded for independence checks.
"""

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

__all__ = [
    "AdapterCapability",
    "AdapterError",
    "AgentAdapter",
    "AgentEvent",
    "AgentResult",
    "AssignmentPacket",
    "EventKind",
    "Registry",
    "get_registry",
    "register_adapter",
]
