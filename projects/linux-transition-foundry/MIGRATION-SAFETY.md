# Data-preserving migration safety contract

## Product boundary
Copies selected Windows user files to separate storage, verifies them, then restores to Ubuntu. It is not a disk image, application converter, OS installer or guarantee that every item has been captured.

## Mandatory gates
- G0 Scope: users, profiles, redirected folders, cloud sync, data owners, retention and required apps.
- G1 Backup medium: separate, capacity-checked, encrypted storage; recovery key held separately.
- G2 Capture: selected folders, junction-safe copy, file sizes and SHA-256 manifest.
- G3 Verification: validate every file, inspect copy errors, open representative files, confirm cloud sync and application exports.
- G4 Install authorisation: explicit approval after backup and rollback evidence. No installer is included.
- G5 Restore: dry-run, new directory, skip collisions, verify copied content.
- G6 Acceptance: user validates data, applications, peripherals, accounts, encryption recovery and workflows.
- G7 Retention: keep Windows and backup until written acceptance and retention policy permit disposal.

Restore rejects absolute/traversal/duplicate paths and checksum/size mismatches. It never deletes source data or overwrites existing destination files. No credential extraction, password-store transfer, browser-cookie migration, certificate/key harvesting, partition changes, bootloader modification or source-disk deletion.

Prototype only. Test disposable VMs with synthetic data and obtain independent security review before any pilot.
