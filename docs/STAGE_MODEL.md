# One Lifecycle, Consistent Progression

Every flow uses the same four-stage lifecycle:

| Stage | Purpose | Gate |
|---|---|---|
| GROUNDING | Establish reality, context, sources, constraints and choose the next coherent increment | Grounding Packet accepted; all Grounding work items complete |
| MOMENTUM | Coordinate execution, building and integration | Candidate and Momentum Packet recorded; all Momentum work items complete |
| MASTERY | Independently challenge the exact candidate | PASS or CONDITIONAL with evidence; FAIL returns to Momentum; BLOCKED pauses |
| REPETITION | Compare intent and outcome, learn and update durable state | Evidence-backed learning packet; complete objective or increment cycle and return to Grounding |

Choosing belongs to Grounding. Building and integration belong to Momentum. Challenge belongs to Mastery. Learning belongs to Repetition. These are not separate workflows.

## Stage is not role

Momentum is a stage, never an agent, department or detached productivity score. Architect, Researcher, Builder and Independent Reviewer are capabilities assigned inside stages. Repetition is a learning stage, not a fourth worker.

## Progress dimensions

- Stage: current lifecycle position.
- Cycle: current pass through the lifecycle.
- Objective progress: accumulated 0–100 outcome progress across cycles; never resets and cannot move backwards.
- Revision: optimistic concurrency version.

Stage movement does not fabricate percentage progress.

## Work graph and gates

Stage-scoped work items have owner role, outcome, acceptance criteria, dependencies and evidence. Dependencies must be completed before dependent work starts. A stage cannot be exited while its work items remain incomplete. Tasks are sub-work inside a flow, not competing lifecycle definitions.

## Recovery

- FAIL returns to Momentum while preserving grounding and candidate history.
- BLOCKED pauses the same stage; unblocking resumes it.
- Stale revisions and stale specialist assignments are rejected.
- Specialist assignments move PROPOSED → ACCEPTED → RUNNING → RETURNED. A return never advances the workflow automatically.
- Two failed attempts against the same hypothesis require root-cause investigation before retry.

## Runtime honesty

The core persists state and dispatch packets. It does not claim to launch independent AI agents by itself. Execution adapters must be configured, permissioned and observable.
