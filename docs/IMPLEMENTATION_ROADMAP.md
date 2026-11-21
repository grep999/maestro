# Maestro Implementation Roadmap

Maestro is built as a project-agnostic orchestrator. Its core lifecycle is
invariant; project adapters and coding presets supply domain context without
redefining progression.

## v0.2 — Operational local core

Implemented:
- Four-stage lifecycle with guarded Grounding, Momentum, Mastery and Repetition
- SQLite persistence, append-only event history, optimistic revision checks
- Stage-scoped work items and dependency gates
- Separate cycle and monotonic objective progress
- Specialist assignment packets with stale-dispatch detection
- CLI, JSON schemas, examples, regression tests

## v0.2.1 — Phase 0 invariant hardening

Implemented:
- Per-cycle packets (cleared on cycle advance; gates reject stale cycle evidence)
- Reviewer independence enforced (builder cannot approve own candidate)
- Candidate binding on review
- Work-item mutations no longer invalidate running assignments
- Transactional stage gates (`BEGIN IMMEDIATE`), microsecond timestamps
- CONDITIONAL requires findings; fail_count + root-cause flag

## v0.3 — Coding out of the box (current)

Implemented:
- **Agent adapter protocol** (`capabilities`, `start`, `stream`, `result`, `cancel`)
- Subprocess adapter + registry (echo + generic CLI agents)
- **Deterministic gate runner** — VERIFIED checks with exit_code + log_hash + SHA
- **Coding module** — git identity, worktree helpers, packet builders, presets
- CLI: `coding-start`, `coding-seed-work`, `adapters`, `adapter-health`, `run-checks`
- Coding examples and out-of-the-box guide

## v0.4 — First-class agent adapters & isolation

- Production adapters: Claude Code, Codex, OpenCode, Gemini CLI, Copilot
- Git worktree lifecycle managed by the control plane
- Sandbox / container isolation + scoped credentials
- Routing policy by role, risk, cost, data class (reviewer ≠ builder by vendor)
- Streaming event persistence into the audit log

## v0.5 — Trust & policy

- Policy-as-code (OPA/Cedar) for path protection and R0–R3 gates
- Signed attestations / hash-chained audit export
- Identity-backed actors (OIDC) so independence is not free-text
- Cost and token budgets with hard stops

## v0.6 — Service operation

- Postgres backend, REST/gRPC API, webhook ingestion (GitHub/GitLab/Linear)
- Multi-user RBAC, SSO, multi-tenancy
- OpenTelemetry, operational runbooks, SOC2-oriented controls

## v0.7 — Portfolio intelligence

- Cross-workflow dependency graph and prioritization
- Eval harness: same task across agents → pass rate, cost, rework
- Repetition stage becomes measurable calibration data
- Forecast vs outcome learning loops

## Release discipline

A stage is complete only when exit criteria have reproducible evidence.
A role prompt is not an independent agent process.
External publication, spending, merge, deploy remain approval-gated.
