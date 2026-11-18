# Implementation status — Linux baseline and migration prototype

## Delivered
- Ubuntu 26.04 LTS primary candidate; 24.04 LTS compatibility fallback.
- Conservative Ansible workstation baseline with package allowlists and firewall opt-in.
- Windows inventory helper.
- Windows user-data backup prototype: Desktop, Documents, Pictures, Music, Videos, Favorites; Downloads is opt-in.
- SHA-256 manifest with relative paths, sizes and source metadata.
- Ubuntu restore utility: manifest verification, dry-run by default, safe relative paths, symlink/path-escape rejection, checksum verification, no overwrite, no source deletion.
- Migration safety contract and initial restore safety tests.
- GitHub Actions workflow already discovers Python unittest tests and performs Ansible syntax validation.

## Evidence status

| Check | Status |
|---|---|
| Source files committed to project branch | PASS |
| Restore safety tests authored | PASS — execution pending |
| Windows PowerShell backup execution | NOT RUN |
| Windows backup/restore round trip | NOT RUN |
| Ansible syntax / CI | PENDING — no run evidence returned |
| Disposable Windows and Ubuntu VM tests | NOT RUN |
| Interrupted-copy and large-file tests | NOT RUN |
| OneDrive/cloud placeholder tests | NOT RUN |
| Encryption and recovery rehearsal | NOT RUN |
| Independent security review | NOT DONE |
| Customer pilot | NOT STARTED |

Do not interpret authored tests as passed. The migration utility is a prototype and must not be used to authorise disk erasure or a production migration.

## Next validation gate
1. Run Python tests in CI and locally.
2. Test Windows backup on a disposable Windows VM with synthetic files, Unicode names, long paths, empty folders, locked files and junctions.
3. Restore to a disposable Ubuntu VM; verify hashes and collision handling.
4. Test interrupted backup recovery, large datasets and cloud-sync placeholders.
5. Review encryption, retention, EFS and application-specific export procedures.
6. Obtain independent security review and rehearse rollback before pilot.

## Release gate
Production readiness requires successful end-to-end evidence, a tested backup/restore and rollback process, hardware/application compatibility, user acceptance and independent security review.
