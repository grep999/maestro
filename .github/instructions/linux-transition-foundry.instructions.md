---
applyTo: "projects/linux-transition-foundry/**"
---

# Linux Transition Foundry review instructions

Review this project as a safety-critical migration tool for moving people and small organisations from Windows to Linux.

## Governing invariants
- Backup must be independent of the source installation and cryptographically verified before installation is authorised.
- Preserve the Windows source and rollback path until the migrated environment is explicitly accepted.
- Never collect or transfer browser passwords, cookies, passkeys, credential stores or secrets automatically.
- No partitioning, bootloader changes, OS installation, source deletion, package mutation, service mutation or reboot without explicit approval.
- Distribution adapters may translate approved intent; they must never grant authorisation.
- Metadata compatibility is not hardware, application, security or workflow compatibility.
- Unknown distribution, version, architecture, package manager, init system or runtime facts must fail closed.
- No automatic acceptance of a task without its required evidence and independent review.

## Required review coverage
1. Trace data handling from inventory through backup, manifest verification, restore and rollback. Look for path traversal, symlink escapes, hash/size mismatches, overwrite hazards and source deletion.
2. Check that privileged operations are absent or separately gated by explicit approval.
3. Check distro IDs, versions, architectures and init-system assumptions against primary distribution documentation. Do not accept distro-name inference for multi-init systems.
4. Check os-release parsing as data only, including quoting, escaping, malformed input and /usr/lib/os-release fallback precedence.
5. Check subprocess calls, shell boundaries, argument construction, permissions and error handling.
6. Check Ansible idempotence, package/service scope, privilege escalation, repository mutation and reboot behavior.
7. Check test coverage for negative paths, unknown facts, unsupported combinations and failure recovery.
8. Check that documentation distinguishes implemented, tested, candidate-only and production-ready capabilities.

## Required review output
- Blocking findings (critical/high/medium), with exact file and line references.
- Non-blocking findings and residual risks.
- Tests/evidence inspected and what remains unverified.
- Explicit verdict: APPROVE, REQUEST_CHANGES or INSUFFICIENT_EVIDENCE.
- Never claim physical-device, live-boot or disposable-VM testing unless artifacts prove it.
