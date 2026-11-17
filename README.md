# Maestro

**Maestro is an independent, project-agnostic workflow orchestration system.** It governs how work moves from intention to verified outcome and how learning compounds across cycles. It is not owned by, embedded in, or defined by any one managed project.

Every flow uses the same lifecycle and progression:

GROUNDING → MOMENTUM → MASTERY → REPETITION → GROUNDING

- **Grounding** establishes reality, sources, constraints, dependencies, uncertainty and the next coherent objective.
- **Momentum** is the delivery stage: coordinated execution, building and integration of the selected increment. It is not an agent or department.
- **Mastery** independently challenges the exact candidate against acceptance criteria and evidence.
- **Repetition** compares intent with outcome, updates durable state and either completes the objective or begins the next cycle.

Choosing belongs to Grounding; building and integration belong to Momentum; challenge belongs to Mastery; learning belongs to Repetition.

## Stage, role and progression are different

| Dimension | Meaning |
|---|---|
| Stage | Position in the shared four-stage lifecycle |
| Role | Capability assigned inside a stage |
| Cycle | Current pass through the lifecycle |
| Objective progress | Accumulated 0–100 outcome progress across cycles; never resets |
| Revision | Optimistic-concurrency version of the workflow |

Architect, Researcher, Builder, Independent Reviewer and Domain Specialist are roles. Momentum is a stage. Repetition is a learning stage and regenerative principle, not a fourth worker.

## Runtime

The first runtime is dependency-free Python 3.10+ with SQLite persistence. One database can hold many unrelated workflows. State transitions are guarded, revisioned and recorded in an append-only event history. Stage-scoped work items have dependency gates. Specialist handoffs cannot advance workflow progression by themselves.

Install and start:

    python -m venv .venv
    . .venv/bin/activate
    pip install -e .
    maestro start sample-project "First workflow" "Deliver a verified outcome"

Use python -m maestro --help for commands. Default database: .maestro/state.sqlite3; override with --db PATH.

## Minimal cycle

    maestro start sample-project "First workflow" "Deliver a verified outcome"
    maestro ground WORKFLOW_ID examples/grounding.example.json --revision 0
    maestro begin-momentum WORKFLOW_ID --revision 1
    maestro deliver WORKFLOW_ID examples/momentum.example.json --revision 2
    maestro submit-mastery WORKFLOW_ID --revision 3
    maestro review WORKFLOW_ID PASS --revision 4 --evidence '["review://evidence"]'
    maestro learn WORKFLOW_ID examples/repetition.example.json --revision 5

Revisions increment on state mutations. Always read current state before a transition; stale writes are rejected. Use show, list, events, add-work, start-work, complete-work, work-items, assign, assignment and assignments for orchestration.

## Repository map

- maestro/ — SQLite-backed state machine and CLI.
- docs/STAGE_MODEL.md — canonical lifecycle, gates and progression.
- docs/SPECIALIST_ROLES.md — capabilities separate from stages.
- docs/ — constitution, research, integration and roadmap.
- .github/agents/ — specialist role contracts.
- .github/workflows/ — deterministic CI validation.
- schemas/ and examples/ — portable task, handoff and workflow contracts.
- projects/ — optional project adapters; Maestro works with this directory empty.
- tests/ — state-machine and persistence regression tests.

## Verify

    python -m unittest discover -s tests -v
    python scripts/validate_contracts.py
    python -m compileall -q maestro scripts tests

## Runtime honesty and safety

The engine persists workflow state and specialist dispatch packets; it does not claim to launch independent AI agents by itself. Execution adapters must be explicitly configured, permissioned and observable. Static checks are not runtime tests. Missing or stale evidence is not PASS. External publication, spending, submissions, sending, merging, deployment and destructive actions require explicit authorization.
