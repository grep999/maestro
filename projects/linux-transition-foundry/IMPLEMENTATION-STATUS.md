# Implementation status — Linux baseline and migration prototype

## Delivered
- Ubuntu 26.04 LTS primary candidate; 24.04 LTS compatibility fallback.
- Conservative Ansible workstation baseline with package allowlists and firewall opt-in.
- Windows inventory helper.
- Windows user-data backup prototype: Desktop, Documents, Pictures, Music, Videos, Favorites; Downloads is opt-in.
- SHA-256 manifest with relative paths, sizes and source metadata.
- Ubuntu restore utility: manifest verification, dry-run default, safe relative paths, symlink/path-escape rejection, checksum verification, no overwrite, no source deletion.
- Migration safety contract and initial restore safety tests.
- GitHub Actions workflow for Python tests and Ansible syntax checks.

## CI evidence — 18 November 2026
- Python unittest discovery: **10 tests passed** (5 baseline safety tests and 5 migration restore tests).
- Ansible collection dependency installation: passed.
- Ansible playbook syntax check: passed.
- Maestro validation workflow: passed.
- GitHub Copilot review request: **not completed**. The workflow received HTTP 422 because the actor does not have a Copilot licence that includes code review, or code review is disabled by organisation policy. This is not an independent code review.

These checks validate Python restore logic and Ansible syntax only. They do not validate PowerShell execution, real Windows backups, actual Ubuntu restore on hardware, application compatibility, encryption or rollback.

## Remaining evidence gaps

| Check | Status |
|---|---|
| Windows PowerShell backup execution | NOT RUN |
| Windows backup/restore round trip | NOT RUN |
| Disposable Windows and Ubuntu VM tests | NOT RUN |
| Interrupted-copy and large-file tests | NOT RUN |
| OneDrive/cloud placeholder tests | NOT RUN |
| Encryption and recovery rehearsal | NOT RUN |
| Independent security review | NOT DONE |
| Customer pilot | NOT STARTED |

Do not interpret authored tests as a production certification. The migration utility is a prototype and must not be used to authorise disk erasure or a production migration.

## Next validation gate
1. Test Windows backup on a disposable Windows VM with synthetic files, Unicode names, long paths, empty folders, locked files and junctions.
2. Restore to a disposable Ubuntu VM; verify hashes and collision handling.
3. Test interrupted backup recovery, large datasets and cloud-sync placeholders.
4. Review encryption, retention, EFS and application-specific export procedures.
5. Obtain an independent security review and rehearse rollback before pilot.

## Release gate
Production readiness requires successful end-to-end evidence, a tested backup/restore and rollback process, hardware/application compatibility, user acceptance and independent security review.
