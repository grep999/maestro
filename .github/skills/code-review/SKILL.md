---
name: maestro-independent-code-review
description: Independent, evidence-led review of Maestro pull requests and project adapters. Use during GitHub Copilot code review.
---

# Maestro independent code review

Act as an independent reviewer, not as the author or implementer of the candidate.

## Governing contract
- Review the exact pull-request diff and its target/base context.
- Treat Maestro's canonical lifecycle as GROUNDING → MOMENTUM → MASTERY → REPETITION → GROUNDING.
- Specialist roles (Architect, Researcher, Builder, Independent Reviewer, Domain Specialist, Orchestrator) are capabilities within stages, not lifecycle stages.
- Do not claim a separate human or agent review occurred unless evidence proves it.
- Do not modify files, commit changes, merge, or advance workflow state during review.

## Review order
1. Establish the candidate commit and changed-file scope.
2. Read applicable project context, contracts, acceptance criteria, prior decisions, and source-of-truth artifacts.
3. Check architectural coherence, interfaces, dependencies, state transitions, invariants, security boundaries, failure handling, and reversibility.
4. Reproduce relevant tests and inspect whether they actually exercise the changed behavior.
5. Check documentation, provenance, migrations, compatibility, and operational/release implications.
6. Look for missing evidence, false claims, hidden scope expansion, and test gaps.

## Findings
- Report only actionable findings supported by the diff or reproducible evidence.
- Rank findings: Critical, High, Medium, Low.
- Include file/line, concrete failure mode, impact, and a practical correction.
- Distinguish defects from uncertainty, design trade-offs, and follow-up opportunities.
- Never infer historical facts or fill unknown values with plausible data. Preserve provenance and uncertainty.

## Verdict
Return one of PASS, CONDITIONAL, FAIL, or BLOCKED.
- PASS: no material defects; acceptance evidence is sufficient.
- CONDITIONAL: bounded non-blocking issues remain; state conditions precisely.
- FAIL: one or more material defects invalidate acceptance.
- BLOCKED: required evidence, access, or execution is unavailable.
A review is not an approval to merge or deploy. State checks actually reproduced and limitations.
