# Copilot review workflow

## Purpose

Use GitHub Copilot code review as the independent MASTERY reviewer for project pull requests. A review request, workflow run or Copilot entitlement warning is not itself a completed review.

## How it is wired

- Workflow: `.github/workflows/copilot-review.yml`
- Repository-wide review instructions: `.github/copilot-instructions.md`
- Project-specific review instructions: `.github/instructions/linux-transition-foundry.instructions.md`
- Trigger: relevant pull request events (opened, reopened, ready for review, new commits) and manual workflow dispatch.
- Review effort is omitted so GitHub applies the effort available to the repository and requesting identity.
- HTTP 409 means a review is already pending.
- HTTP 422 is reported as an unavailable review, not a code-test failure. The Maestro MASTERY gate remains blocked.

## Enable an eligible requesting identity

The current workflow's `GITHUB_TOKEN` request returned HTTP 422 because GitHub reported that the actor lacks an eligible Copilot code-review entitlement or the organisation policy disables the feature.

To use an eligible user identity:

1. Create a fine-grained personal access token owned by a GitHub user who can request Copilot code review for this repository.
2. Grant repository access to `grep999/maestro` and **Pull requests: read and write** permission.
3. Add it to repository Actions secrets as `COPILOT_REVIEW_TOKEN`.
4. Keep the workflow's `GITHUB_TOKEN` fallback only for transparent entitlement diagnostics; it cannot bypass Copilot licensing or organisation policy.
5. If the token owner is not eligible, ask the organisation owner to enable Copilot code review for members and confirm billing/entitlement configuration.

Do not commit the token, place it in workflow YAML, or expose it in logs. This repository's available GitHub integration does not expose Actions-secret management, so the secret must be configured in GitHub repository Settings by an authorised user.

## Request a review

- Relevant PR updates automatically request a Copilot review.
- To retry a specific PR manually: Actions → Request GitHub Copilot review → Run workflow → enter the PR number.
- A successful API response means the request was created, not that review completed.
- Inspect the PR for Copilot-attributed review comments or a submitted Copilot review.

## MASTERY acceptance

A task may leave `VERIFYING` only after:
- The exact candidate SHA is identified.
- Required CI evidence is green for that SHA.
- Copilot's review artifact exists and has been inspected.
- Findings are fixed or explicitly dispositioned with evidence.
- Any required human/domain review and VM/live-boot validation are complete.

If Copilot is unavailable, record `INSUFFICIENT_EVIDENCE`; do not simulate a Copilot review with a Builder self-review or a static workflow check.
