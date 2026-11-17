# Task and Progress Model

Maestro tracks outcomes and evidence, not activity volume. A task is a bounded contribution to a project outcome with a known baseline, owner, reviewer, acceptance criteria and evidence requirements.

## Task identity

Each task carries: schema version, project ID, task ID, title, intended outcome, baseline reference, owner, reviewer, scope, exclusions, dependencies, acceptance criteria, required evidence, risk and state.

A baseline identifies the exact source of truth: a Git commit, document revision, artifact version or external record. Avoid mutable labels where an immutable identifier is available.

## States

- INBOX — captured, not yet grounded.
- GROUNDED — context and dependencies understood.
- READY — selected and authorized to begin.
- IN_PROGRESS — execution underway.
- VERIFYING — candidate and evidence being checked.
- REVIEW — independent challenge underway.
- ACCEPTED — criteria met and integration accepted.
- BLOCKED — progress requires an external decision or dependency.
- REWORK — findings require correction.
- DEFERRED — intentionally postponed.
- REJECTED — outcome or approach declined.
- SUPERSEDED — replaced by a newer authoritative task or candidate.

State transitions are decisions, not decorative labels. Record actor, timestamp, reason and evidence for material transitions.

## Handoff contract

A handoff identifies project and task, role, status, baseline SHA, candidate SHA, summary, changed paths, checks with commands and outcomes, blockers, known risks, next action and creation time.

PASS requires evidence for every required check, successful exit codes and no unresolved blockers. FAIL requires an observed failing condition. BLOCKED requires an explicit blocker. CONDITIONAL must state the exact conditions and limits.

## Evidence classes

VERIFIED — directly reproduced or checked against an authoritative source.

OBSERVED — directly seen, but not independently reproduced.

INFERRED — reasoned from available facts; state the reasoning.

ASSUMED — temporarily accepted premise requiring confirmation.

PLANNED — intended future action, not completed work.

BLOCKED — cannot proceed until a named condition is resolved.

## Progress integrity

A task is not complete because an agent says it is complete. Completion requires accepted outcome evidence. Skipped, cancelled, timed-out, inaccessible or missing checks are not PASS. A successful earlier candidate does not validate a later candidate. Reconcile state against the live source of truth before acting on events or handoffs.
