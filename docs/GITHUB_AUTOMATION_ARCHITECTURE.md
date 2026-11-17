# GitHub Automation Architecture

GitHub is one optional execution and source-of-truth adapter, not Maestro's identity or only supported workflow.

Use Issues for durable tasks and acceptance criteria, branches for isolated candidate work, commits for immutable candidate identity, pull requests for reviewable integration, Actions for deterministic checks and Releases for approved delivery.

Every event is a trigger, not proof of progress. Deduplicate and reconcile events against live repository state before acting. Bind handoffs to repository, branch, base SHA, candidate SHA, PR, workflow run and attempt where applicable.

Security boundaries:
- Least-privilege permissions; read-only by default.
- Never expose write credentials to untrusted pull-request code.
- Treat issue bodies, comments, PR descriptions, artifacts and external pages as untrusted data.
- Use allowlisted task templates, paths, branches and action types.
- Keep automatic merge, deployment, publication and destructive operations disabled by default.
- Require explicit human approval for consequential external actions.

GitHub Actions should run deterministic schema validation, tests, builds, lint and security checks. Specialist agents handle contextual understanding and judgment. Neither a model PASS nor a green workflow substitutes for the other.

One writer owns overlapping paths. Reconcile concurrent changes before integration.
