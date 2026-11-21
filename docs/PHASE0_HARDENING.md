# Phase 0 Hardening (v0.2.1)

Applied after a full source review that confirmed several state-machine invariants were not enforced at runtime.

## Critical fixes

1. **Per-cycle packets**  
   Stage packets (`grounding`, `momentum`, `mastery`) are tagged with `_cycle` and cleared on cycle advance (`learn` → new GROUNDING). `begin_momentum` and `submit_mastery` reject packets that do not belong to the current cycle. Cycle 2+ can no longer ride on cycle 1 evidence.

2. **Reviewer independence**  
   The actor who `deliver`s a candidate is recorded as `builder_actor`. `review` rejects any actor that matches the builder (case-insensitive). This is the product's headline promise and is now enforced.

3. **Candidate binding**  
   `review(..., candidate_ref=...)` optionally or implicitly binds to the exact `candidate_ref` that was submitted. Mismatch raises. A candidate marked `_submitted` cannot be silently overwritten by another `deliver` of the same ref until a FAIL returns the workflow to Momentum.

4. **Work-item / assignment isolation**  
   Adding or completing work items no longer increments the workflow `revision` used by stage transitions and assignment stale-checks. Assignments are considered stale only when stage, cycle, or status diverge — not when unrelated work items appear. Parallel agents no longer collide on every work-item touch.

5. **Transactional stage gates**  
   All check-and-write paths use `BEGIN IMMEDIATE`. Stage and packet validation happen inside the write transaction (no TOCTOU on `_stage_clear`).

6. **Timestamps**  
   Microsecond ISO-8601 timestamps. Ordering ties broken by primary key / `id`.

7. **CONDITIONAL & two-failure rule**  
   `CONDITIONAL` requires non-empty findings (tracked conditions). Consecutive FAILs increment `fail_count`; on the second FAIL the mastery packet carries `requires_root_cause: true`.

## Remaining (Phase 1+)

- Real agent adapter protocol and sandboxed execution.
- Deterministic gate runner (agents must not self-report check outcomes).
- Authenticated identities for actors (SSO) so independence is identity-based, not free-text.
- JSON Schema validation wired into the engine and `validate_contracts.py`.
- Service layer, multi-tenancy, OTel, cost budgets.

## Test coverage

15 unit tests, including dedicated cases for cycle-packet hygiene, reviewer independence, candidate binding, and assignment isolation under work-item churn.
