# Repository status

This repository is the project-agnostic Maestro core. It contains the reusable operating constitution, four-pillar model, three specialist role contracts, task and handoff schemas, examples, validation tooling and integration/implementation guidance.

## Independence boundary

- Maestro does not belong to, depend on, or inherit its purpose from any one managed project.
- No managed project's source code, backlog, product identity, domain rules or private working records belong in the Maestro core.
- Project-specific context is supplied through optional adapters and remains owned by the respective project.
- The core must remain valid and operable with an empty `projects/` directory.

## Verification

Run `python3 scripts/validate_contracts.py` from the repository root. A successful local validation establishes only that the included contracts/examples pass that validator; it does not establish that external integrations, agents, workflows or project deliverables are running.

## Remote publication

This is a local repository payload. It is not evidence of a remote Git commit. Remote publication must be verified against the target repository after a successful write.
