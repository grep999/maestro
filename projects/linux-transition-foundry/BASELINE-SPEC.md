# Linux Office Baseline 1.0 — specification

Status: implementation candidate; not yet validated on physical hardware.

## Supported platform policy

- Primary candidate: Ubuntu Desktop 26.04 LTS amd64, subject to pilot validation.
- Compatibility fallback: Ubuntu Desktop 24.04 LTS where application, hardware or vendor constraints require it and the customer accepts the remaining support horizon.
- Reassess distribution choice at each customer engagement; do not silently upgrade major releases.
- Pin the tested point-release image, package manifest and configuration revision in each deployment record.

Ubuntu's published release lifecycle lists 26.04 LTS standard support through May 2031 and 24.04 LTS through May 2029. Verify lifecycle dates and package availability before each customer deployment.

## Baseline outcomes

1. Reproducible workstation configuration.
2. Least-privilege local administration.
3. Supported security updates.
4. Disk encryption selected at installation after recovery-key custody is agreed.
5. Host firewall policy appropriate to endpoint role.
6. Approved software catalogue.
7. Central identity integration only after customer-specific validation.
8. Backup and recovery procedure tested.
9. Inventory and operational telemetry proportionate to privacy requirements.
10. Documented Windows application exceptions.

## Configuration policy

- Ansible is the configuration automation candidate.
- Default playbook must be non-destructive and must not partition disks, create users, modify identity integration, enable a firewall, reboot, or remove packages without explicit variables and a reviewed change plan.
- Package installation is allowlisted and profile-driven.
- Check mode and diff mode are supported where Ansible modules permit.
- Secrets are never committed to Git; use an approved secret manager or Ansible Vault.
- Customer-specific values live outside the generic baseline.

## Profiles

- office: browser, document editing, PDF and common utilities.
- engineering: office plus approved developer tooling.
- kiosk/shared: separately designed restricted profile; not covered by the initial workstation role.

## Acceptance

- Syntax checks and lint pass.
- Idempotence demonstrated on a disposable VM.
- Re-run produces no unintended changes.
- Check mode reviewed.
- Update, reboot and recovery procedures documented.
- Disk encryption recovery tested on supported hardware.
- Security controls verified rather than inferred from configuration.
