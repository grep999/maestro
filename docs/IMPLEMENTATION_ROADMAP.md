# Maestro Implementation Roadmap

Maestro is built as a project-agnostic orchestrator. Its core lifecycle is invariant; project adapters supply domain context without redefining progression.

## v0.2 — Operational local core

Implemented:
- Four-stage lifecycle with guarded Grounding, Momentum, Mastery and Repetition transitions.
- SQLite persistence, append-only event history and optimistic revision checks.
- Stage-scoped work items and dependency gates.
- Separate cycle and monotonic objective progress.
- Specialist assignment and return packets with stale-dispatch detection.
- CLI, JSON schemas, examples and regression tests.
- GitHub Actions validation for contracts, tests and compilation.

## v0.3 — Execution adapters

- Adapter protocol for GitHub, documents, research and external project systems.
- Capability discovery and permission-scoped dispatch.
- Durable run records, retries, idempotency and cancellation.
- Execution telemetry and observable handoff state.
- Independent reviewer isolation and conflict-of-interest rules.

## v0.4 — Orchestration intelligence

- Dynamic role composition based on task requirements and evidence gaps.
- Cross-workflow dependency graph and portfolio-level prioritization.
- Recovery plans for stale sources, interrupted work and unavailable tools.
- Forecast versus outcome calibration and risk learning.

## v0.5 — Service operation

- API service and authenticated clients.
- Multi-user ownership, access control and audit export.
- Backups, migrations, observability and operational runbooks.
- Deterministic release process and compatibility guarantees.

## Release discipline

A stage is complete only when exit criteria have reproducible evidence. A configured workflow is not a successful run. A role prompt is not an independent agent process. External publication, spending, submissions, sending, merging, deployment and destructive actions remain approval-gated.
