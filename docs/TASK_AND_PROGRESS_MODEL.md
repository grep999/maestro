# Task, Flow and Progress Model

Each project can have multiple independent workflows; all share one lifecycle and transition contract.

## Four distinct dimensions

- Stage: GROUNDING, MOMENTUM, MASTERY or REPETITION.
- Role: Architect, Researcher, Builder, Independent Reviewer, Domain Specialist or Orchestrator.
- Cycle: current pass through the lifecycle.
- Objective progress: accumulated outcome progress from 0–100. It is updated during Repetition and cannot move backwards or reset between cycles.
- Revision: optimistic-concurrency version. Stale writes are rejected.

## Work items and dependencies

Work items are bounded pieces of stage work, not separate workflows. Each has an owner role, outcome, acceptance criteria, dependencies, status and evidence. Dependencies must be complete before dependent work starts. A stage cannot be exited while its work items remain incomplete.

## Stage gates

| Stage | Exit gate |
|---|---|
| GROUNDING | Grounding Packet accepted; Grounding work items complete |
| MOMENTUM | Candidate and Momentum Packet recorded; Momentum work items complete |
| MASTERY | Independent verdict with evidence; FAIL returns to Momentum; BLOCKED pauses |
| REPETITION | Learning packet with evidence; complete objective or increment cycle and return to Grounding |

## Specialist handoffs

A dispatch packet binds workflow ID, project ID, stage, workflow revision, role, capability, expected output and least-privilege boundary. Its lifecycle is PROPOSED → ACCEPTED → RUNNING → RETURNED. A returned handoff does not advance the workflow; the orchestrator reconciles it and invokes the stage gate. If stage or revision changes, the assignment is stale.

## Evidence

VERIFIED is reproduced or checked against an authoritative source. OBSERVED is directly seen but not independently reproduced. INFERRED is reasoned from facts. ASSUMED is provisional and requires confirmation. PLANNED is future work. BLOCKED requires a named condition.

Skipped, timed-out, inaccessible or missing checks are not PASS. A successful earlier candidate does not validate a later candidate.
