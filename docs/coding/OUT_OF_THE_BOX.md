# Coding out of the box

Maestro is a **control plane**, not another coding agent. It makes agentic
coding *auditable*: every increment is grounded, built in isolation, challenged
by an independent party, and learned from.

## 30-second path

```bash
# from a git checkout of your project
python -m venv .venv && . .venv/bin/activate
pip install -e /path/to/maestro

maestro coding-start my-app "Add /health" "Expose /health with tests" --risk R1
# → workflow id + grounded packet bound to your HEAD SHA

maestro begin-momentum WORKFLOW_ID --revision N
maestro coding-seed-work WORKFLOW_ID --revision N
# → research / implement / gate work items

# assign a builder (any adapter: claude-code, codex, opencode, echo, …)
maestro assign WORKFLOW_ID BUILDER implementation '{"deliverable":"health endpoint"}'
maestro adapters   # see registered agent adapters

# after the agent returns a candidate SHA + changed paths:
maestro deliver WORKFLOW_ID examples/coding/momentum.feature.json --revision N
maestro submit-mastery WORKFLOW_ID --revision N

# independent reviewer (must be a different actor than the builder)
maestro review WORKFLOW_ID PASS --revision N \
  --evidence '["review:diff","gate:unit-tests"]' \
  --actor reviewer-bot --candidate-ref artifact:health-endpoint-v1

maestro learn WORKFLOW_ID examples/coding/repetition.feature.json --revision N
```

## What "verified" means here

| Claim | Trusted source |
|-------|----------------|
| Checks passed | `GateRunner` executed the command, recorded `exit_code` + `log_hash` on a specific SHA (`evidence_class: VERIFIED`) |
| Reviewer independence | Engine rejects review when `actor == builder_actor` |
| Candidate identity | Review binds to the exact `candidate_ref` / SHA submitted at Mastery |
| Cycle hygiene | Packets are cycle-scoped; cycle N+1 cannot reuse cycle N evidence |

Agent self-reported checks are **ASSUMED** until the gate runner verifies them.

## Risk tiers (task schema R0–R3)

| Tier | Typical use | Gates |
|------|-------------|-------|
| R0 | Docs, comments, pure refactors with tests | Optional independent review |
| R1 | Feature work behind flag / non-critical path | Required independent review + unit gates |
| R2 | Auth, payments, data migration | Human approval + broader gates + reviewer identity separation by vendor |
| R3 | Production config, secrets, destructive ops | Explicit human authorization; Maestro will not auto-merge/deploy |

## Adapter protocol

```text
capabilities() → what roles / isolation / identity
start(packet)  → run_id
stream(run_id) → AgentEvent…
result(run_id) → AgentResult  (status, evidence, candidate_sha, checks, …)
cancel(run_id)
```

Register adapters with `register_adapter("claude-code", factory)`. Prefer
**different** `model_identity` for BUILDER vs INDEPENDENT_REVIEWER.

## Isolation defaults

- One git worktree + branch per Momentum candidate
- Short-lived credentials; network allowlist when sandboxed
- Permission boundary: `least_privilege` unless risk policy elevates

## Design stance

Most agent launchers optimize for throughput. Maestro optimizes for
**verifiable outcomes and compounding learning**. That is the enterprise gap
this control plane is built to fill.
