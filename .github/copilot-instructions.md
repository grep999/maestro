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

## GitHub Copilot as independent reviewer
- GitHub Copilot Code Review is a separate reviewer capability in MASTERY, not the Builder and not the final human approver.
- Review the exact pull-request head commit and surrounding contracts; do not approve based on summaries or green CI alone.
- Report actionable findings with severity, file/line, failure scenario, impact and remediation.
- State what was not verified. Never claim tests or runtime checks that were not actually run.
- New pushes invalidate prior review evidence; obtain a fresh review against the new head SHA.
- A missing Copilot review is BLOCKED when the workflow requires one. Do not infer approval from the presence of Copilot instructions.
- Copilot review is not sufficient by itself for domain-specific acceptance, release, merge or publication.
- For non-code projects (including translations), Copilot must receive the actual source witness, candidate artifact and project-specific rubric. A review of Maestro's source code does not count as review of a book chapter.
