# Independent Review — GitHub Copilot

## Purpose

Maestro separates delivery from challenge. GitHub Copilot Code Review is an independent reviewer for pull requests; it inspects the candidate after the builder submits it and before the workflow can record MASTERY as PASS.

## Operating protocol

1. Builder completes a scoped increment and opens a pull request.
2. CI runs deterministic tests, contract validation, formatting and static checks.
3. Request GitHub Copilot Code Review on the pull request, or enable automatic review through a repository ruleset.
4. Copilot reviews the exact head commit using `.github/copilot-instructions.md`.
5. Builder addresses findings in new commits; every new push must receive a fresh review.
6. Maestro records the review URL, reviewed head SHA, findings, disposition and verification evidence.
7. The Independent Reviewer challenges the fixes. Only then may MASTERY be recorded PASS.
8. A human maintainer makes final merge and release decisions.

## Required evidence record

- Pull request URL and repository
- Head commit SHA reviewed
- Copilot review URL/ID and timestamp
- Findings grouped by blocking / non-blocking / informational
- Each finding's disposition and fix commit, or explicit human acceptance rationale
- CI run URL and exact checks/results
- Remaining limitations and final gate decision

## Configuration

Repository administrators can enable automatic Copilot reviews with a branch ruleset and choose review on new pushes and draft pull requests. Configure a ruleset targeting the intended development branches and enable **Automatically request Copilot code review** plus **Review new pushes**. Keep Copilot approvals from counting as the sole merge approval; human acceptance remains required.

Copilot Code Review availability and automatic-review entitlements depend on the repository/account plan and repository policy. If automatic review is unavailable, request it manually from the pull request's Reviewers menu. A missing review is a BLOCKED gate, not an assumed pass.

## Scope limitation

This integration makes Copilot a reviewer of Maestro repository pull requests. It does not, by itself, give Copilot access to Radha Library documents or independently proofread book chapters. For Radha, each chapter must be provided in a dedicated reviewable artifact/PR or another explicitly connected review surface, with the source witness and chapter-specific review rubric attached. Do not report a book chapter as independently reviewed merely because Copilot reviewed Maestro's code.
