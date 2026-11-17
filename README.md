# Maestro

**Maestro is an independent, project-agnostic workflow orchestration system.** It coordinates work from intention to verified outcome and compounds learning across cycles. It is not an application, studio, or workflow belonging to any one project.

Maestro can govern software engineering, research, product development, creative production, operations, grant work, organizational programmes, or mixed-discipline initiatives. The domain changes; the orchestration principles remain stable.

## Governing cycle

`GROUND → CHOOSE → BUILD → CHALLENGE → INTEGRATE → LEARN → GROUND`

- **Grounding** establishes the real situation: intent, source of truth, context, constraints, dependencies, uncertainty, risks and evidence.
- **Momentum** selects and delivers the highest-leverage coherent increment.
- **Mastery** independently challenges the exact candidate against explicit acceptance standards and evidence.
- **Repetition** is the regenerative learning principle, not a fourth worker and never a blind retry.

The orchestrator holds the whole: purpose, priorities, shared state, task graph, sequencing, decision rights and permission boundaries. Specialist functions are composed to fit the work; they are not a fixed department chart. A role definition is not proof of a running independent agent.

## Repository map

- `docs/` — constitution, operating model, four pillars, task/progress model, integration architecture, research and roadmap.
- `.github/agents/` — reusable Grounding, Momentum and Mastery role contracts.
- `.github/workflows/` — repository-level contract validation.
- `schemas/` and `examples/` — portable task and handoff contracts.
- `scripts/` — local validators.
- `projects/` — optional project adapters and configurations; no project is privileged or required.
- `projects/PROJECT_ADAPTER_TEMPLATE.md` — starting point for connecting any project to Maestro.

## Apply Maestro to a project

1. Establish the project's actual purpose, stakeholders, source of truth, constraints and definition of success.
2. Create a project adapter using `projects/PROJECT_ADAPTER_TEMPLATE.md`; keep domain-specific rules and records in the project itself.
3. Map existing work, decisions, evidence, dependencies and approval boundaries. Do not duplicate canonical state unnecessarily.
4. Select one coherent increment, execute it through Momentum, and submit the exact candidate to independent Mastery review.
5. Integrate only against explicit acceptance criteria; record what changed and what was learned.

A project adapter is configuration and context, not a fork of Maestro. Maestro must remain useful when the `projects/` directory is empty.

## Evidence and safety

Use `VERIFIED`, `OBSERVED`, `INFERRED`, `PLANNED` and `BLOCKED` precisely. Static checks are not runtime tests. A configured workflow is not a CI pass. Missing or stale evidence does not pass. After two failed attempts against the same unchanged hypothesis, stop and investigate root cause.

Research, analysis, drafting, local edits and safe tests may proceed within granted authority. External publication, spending, submission, sending, merging, deployment and destructive changes require the relevant explicit approval.

## Validate the contracts

```bash
python3 scripts/validate_contracts.py
```
