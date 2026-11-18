# Implementation status — Linux Office Baseline 1.0

## Delivered in this increment

- Candidate platform policy documented: Ubuntu 26.04 LTS primary candidate; 24.04 LTS compatibility fallback.
- Conservative Ansible workstation role with package allowlists.
- Firewall management disabled by default and requires explicit opt-in.
- Automatic security-update configuration is enabled by default.
- Empty lab inventory; no target host is configured.
- No disk partitioning, OS installation, identity enrolment, account creation, reboot or destructive operations.
- Python safety-contract tests.
- Repository-level GitHub Actions workflow for safety tests and Ansible syntax validation.

## Evidence status

| Check | Status |
|---|---|
| Files committed to project branch | PASS |
| Static safety contract authored | PASS — execution pending |
| Ansible syntax workflow authored | PASS — execution pending |
| Disposable VM deployment | NOT RUN |
| Idempotence test | NOT RUN |
| Hardware/peripheral validation | NOT RUN |
| Disk encryption and recovery test | NOT RUN |
| Identity integration | NOT IMPLEMENTED |
| Customer pilot | NOT STARTED |

The GitHub connector did not return any workflow runs for the latest commit. Therefore CI must be treated as pending, not passed. Execute the workflow in GitHub Actions or run the documented commands locally before treating the baseline as validated.

## Immediate next steps

1. Run safety tests and Ansible syntax validation.
2. Provision a disposable Ubuntu 26.04 LTS VM and validate package names/service units.
3. Test Ansible check mode, first application and second idempotent application.
4. Add explicit identity, backup, monitoring and endpoint-enrolment adapters only after requirements are defined.
5. Validate disk encryption during installation and rehearse recovery-key handling.
6. Obtain independent security review before pilot use.

## Release gate

Do not label this baseline production-ready until the VM tests, recovery tests, security review, hardware compatibility matrix and pilot acceptance criteria are complete.
