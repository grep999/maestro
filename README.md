# Maestro

**Agent-agnostic workflow control plane for verified coding outcomes.**

Maestro governs how work moves from intention → isolated candidate → independent
challenge → learned next cycle. It does not embed a coding agent. It orchestrates
whatever agents you already trust (Claude Code, Codex, OpenCode, Gemini CLI,
Copilot, local models, custom CLIs) under a strict lifecycle:

```text
GROUNDING → MOMENTUM → MASTERY → REPETITION → GROUNDING
```

- **Grounding** establishes reality, sources, constraints, and the next coherent increment
- **Momentum** is coordinated execution and integration (not a role or a score)
- **Mastery** independently challenges the *exact* candidate against acceptance + evidence
- **Repetition** compares intent vs outcome, updates durable state, and compounds learning

Stage ≠ role. Progress is monotonic. Evidence has classes. External actions stay
approval-gated. The engine is honest about what it does *not* do: it does not
launch agents by itself — adapters do.

## Why this exists

The market is full of agent *launchers*. Few are trustworthy *governors*.
Maestro’s niche is the neutral control plane that proves what an agent did and
whether an independent party verified it — suitable for real project coding work
out of the box.

## Install

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
```

Python 3.10+, zero runtime dependencies. Default DB: `.maestro/state.sqlite3`.

## Coding out of the box

```bash
# Ground a workflow in the current git repo
maestro coding-start my-app "Add /health" "Expose /health with unit tests" --risk R1

# Move to delivery and seed standard work items
maestro begin-momentum <WORKFLOW_ID> --revision <N>
maestro coding-seed-work <WORKFLOW_ID> --revision <N>

# List agent adapters / probe health
maestro adapters
maestro adapter-health --name echo

# Run deterministic gates (VERIFIED evidence with log hashes)
maestro run-checks --workspace . --preset python

# Full lifecycle still works via explicit packets
maestro ground <ID> examples/coding/grounding.feature.json --revision 0
maestro deliver <ID> examples/coding/momentum.feature.json --revision <N>
maestro submit-mastery <ID> --revision <N>
maestro review <ID> PASS --revision <N> --evidence '["review:ok"]' --actor reviewer-bot
maestro learn <ID> examples/coding/repetition.feature.json --revision <N>
```

See [docs/coding/OUT_OF_THE_BOX.md](docs/coding/OUT_OF_THE_BOX.md) for the full path.

## Core guarantees (v0.3.0)

| Guarantee | Enforcement |
|-----------|-------------|
| Cycle isolation | Packets tagged by cycle; cleared on cycle advance |
| Reviewer independence | `review` rejects when actor equals builder |
| Candidate binding | Review must match submitted `candidate_ref` |
| Assignment stability | Work-item churn does not invalidate running assignments |
| Append-only audit | SQL triggers block update/delete on events |
| Optimistic concurrency | Stale revisions rejected |
| Gate trust | `GateRunner` produces `VERIFIED` checks with exit code + log hash |

## Architecture surface

```text
maestro/
  engine.py          # durable state machine (SQLite)
  coding.py          # git identity, worktree helpers, packet builders, presets
  checks.py          # deterministic gate runner
  adapters/
    protocol.py      # AgentAdapter contract
    subprocess_adapter.py
  cli.py
```

## Adapter protocol (agent-agnostic)

```python
capabilities() → AdapterCapability
start(AssignmentPacket) → run_id
stream(run_id) → Iterator[AgentEvent]
result(run_id) → AgentResult
cancel(run_id)
```

Register with `register_adapter("name", factory)`. Prefer different
`model_identity` for builder vs independent reviewer.

## Runtime

```bash
maestro start sample-project "First workflow" "Deliver a verified outcome"
python -m maestro --help
```

One database can hold many unrelated workflows. State transitions are guarded,
revisioned, and recorded in an append-only event history.

## Repository map

- `docs/` — constitution, stage model, roles, roadmap, coding guide
- `schemas/` — portable task / handoff / workflow contracts
- `examples/` + `examples/coding/` — packets you can run today
- `tests/` — state machine + adapter + gate coverage
- `projects/` — optional adapters; core works with this directory empty

## Verify

```bash
python -m unittest discover -s tests -v
python scripts/validate_contracts.py
python -m compileall -q maestro scripts tests
```

## Safety stance

External publication, spending, merge, deploy, and destructive actions require
explicit authorization. Missing evidence is not PASS. Static checks are not
runtime tests. Events are triggers, not proof — reconcile against live state.

The engine persists workflow state and specialist dispatch packets; it does not
claim to launch independent AI agents by itself. Execution adapters must be
explicitly configured, permissioned, and observable.

## License

MIT
