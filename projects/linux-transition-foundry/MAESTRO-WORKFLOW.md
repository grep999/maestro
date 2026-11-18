# Linux Transition Foundry — Maestro workflow record

This is a portable project-side workflow record. The authoritative Maestro runtime state remains in its SQLite database; this file does not impersonate a runtime transition or invent a workflow ID/revision.

## Lifecycle

GROUNDING → MOMENTUM → MASTERY → REPETITION → GROUNDING

- Grounding: established current branch, baseline, constraints, sources and next increment.
- Momentum: implement the distribution adapter contract and its tests.
- Mastery: independent review of the exact candidate and evidence.
- Repetition: compare outcome with acceptance, record lessons and choose the next increment.

## Current grounding

- Repository: grep999/maestro
- Project branch: project/linux-transition-foundry
- Project pull request: #4, open/draft, unmerged.
- Baseline before this increment: cbd5c91f0f1a5682604a807fd21ede46d8f65b51
- Project objective: data-safe Windows-to-Linux migration with hardware-appropriate distro selection and validated office workflows.
- Safety constraints: verified independent backup before installation; no credential/browser-secret transfer; no partitioning, bootloader changes, OS installation, source deletion, package mutation, service mutation or reboot without a separate explicit approval.
- Evidence limits: no local clone, Windows host, physical test device or disposable VM is available in this execution environment. GitHub CI is not yet evidenced for the preceding commit.

## Selected next increment

The adapter metadata and fail-closed policy are implemented. The next Momentum increment adds a read-only runtime discovery tool that parses distro identity/version, CPU architecture, APT availability and actual PID 1. It produces a compatibility report only; no package or service operations are executed.

## Acceptance

1. Every distro recommender profile has exactly one adapter metadata entry.
2. Multi-init distributions use runtime detection; distro name alone never selects the service manager.
3. Unknown runtime facts block all mutation.
4. Package/service mutation and reboot remain disabled by default.
5. Adapter metadata and tests are included in CI.
6. The exact commit is reviewed independently before claiming acceptance.

## Role assignments (capabilities, not claims of spawned agents)

- Architect: define engine/adapter boundary and failure semantics.
- Researcher: verify distro/init facts from primary project documentation.
- Builder: implement metadata contract, tests and CI integration.
- Independent Reviewer: challenge the exact candidate; no review is claimed until a review artifact exists.
- Orchestrator: preserve branch boundaries, gate transitions and record evidence.

## Copilot independent review integration

- Repository workflow: `.github/workflows/copilot-review.yml` requests Copilot code review on relevant PR events and supports manual dispatch for a selected PR.
- Review guidance: `.github/copilot-instructions.md` and `.github/instructions/linux-transition-foundry.instructions.md` define repository and project-specific review criteria.
- Setup and acceptance instructions: `COPILOT-REVIEW.md`.
- The previous `GITHUB_TOKEN` request returned HTTP 422 because the requesting actor/repository was not eligible under Copilot licensing or organisation policy. The workflow now supports `COPILOT_REVIEW_TOKEN` as an eligible user's fine-grained token and reports entitlement failure without disguising it as a code-test failure.
- The GitHub integration available to this execution cannot configure repository Actions secrets. An authorised repository user must add `COPILOT_REVIEW_TOKEN` in GitHub Settings → Secrets and variables → Actions.
- A request or pending status is not a completed review. The task remains VERIFYING until Copilot review output exists and is assessed.

## Next cycle after this increment

First obtain an eligible Copilot review request and inspect its review artifact; keep both tasks in VERIFYING until findings and evidence are resolved. If accepted, implement the read-only package availability planner; do not yet execute package or service mutations.
