# Maestro repository instructions

## Canonical workflow
Preserve the lifecycle GROUNDING → MOMENTUM → MASTERY → REPETITION → GROUNDING. Momentum and Repetition are stages, not agents. Architect, Researcher, Builder, Independent Reviewer, Domain Specialist and Orchestrator are specialist capabilities within stages.

## Repository architecture
- Maestro's core engine, contracts, workflow state and validation remain at repository root.
- Each product or client project must live on its own dedicated branch and under an isolated directory such as `projects/<project-name>/`.
- Do not mix project-specific implementation commits into Maestro's core workflow-design changes.
- Do not make the core engine depend on any individual project adapter.
- Project work should be integrated through a dedicated branch and reviewed PR; do not push unrelated projects to the default branch.

## Quality and governance
- Never fabricate test results, tool execution, reviews, evidence or workflow transitions.
- Independent Reviewer must not author or silently repair the candidate being reviewed.
- A review must identify the exact candidate SHA, evidence, severity-ranked findings, checks reproduced and limitations.
- Missing evidence is BLOCKED, not PASS.
- Preserve source provenance, uncertainty and unknown values.
- Keep consequential actions such as merge, release, deployment, publication and spending behind explicit authorization.
