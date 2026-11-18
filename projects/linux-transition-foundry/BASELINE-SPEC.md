# Linux workstation baseline — distribution-flexible specification

Status: implementation candidate; not validated on physical hardware.

## Distribution policy

Distribution choice is hardware- and workload-driven, not ideological. Ubuntu Desktop 26.04 LTS remains the standard candidate for capable machines. Lightweight alternatives are first-class supported candidates; no device is forced onto GNOME.

Curated profiles and selection thresholds are maintained in DISTRIBUTION-MATRIX.md. The current catalogue includes Ubuntu Desktop, Linux Mint Xfce, Xubuntu, Lubuntu, MX Linux Xfce, Debian with LXQt and antiX.

The recommender uses physical RAM and CPU architecture as an initial filter only. It does not establish compatibility. The final selection requires a live-USB hardware test, application/workflow test, support-lifecycle check and customer approval.

## Hardware selection bands

- 6 GB+ RAM: Ubuntu GNOME eligible; lighter desktops remain options.
- 4–6 GB: Mint Xfce or Xubuntu preferred.
- 2–4 GB: Lubuntu or Xubuntu preferred; Mint Xfce evaluated.
- 1–2 GB: MX Xfce or Debian LXQt; antiX for constrained legacy workloads.
- 512 MB–1 GB: antiX legacy exception only; modern browser-based office work may be impractical.
- Below 512 MB: no supported office recommendation; evaluate replacement or narrow single-purpose use.
- 32-bit x86: antiX is the only curated candidate; verify maintained application availability before proceeding.

These are conservative product selection thresholds, not official installer minimums. See source notes in DISTRIBUTION-MATRIX.md.

## Baseline outcomes

1. Reproducible workstation configuration.
2. Least-privilege local administration.
3. Supported security updates and documented lifecycle.
4. Disk encryption selected at installation after recovery-key custody is agreed.
5. Host firewall policy appropriate to endpoint role.
6. Approved software catalogue.
7. Central identity integration only after customer-specific validation.
8. Backup and recovery procedure tested.
9. Inventory and operational telemetry proportionate to privacy requirements.
10. Documented Windows application exceptions.

## Configuration policy

- Ansible is the configuration automation candidate.
- Distribution-specific roles and package maps must be explicit; never assume Ubuntu package names or service names work unchanged on Debian, MX or antiX.
- Default playbooks must be non-destructive and must not partition disks, create users, modify identity integration, enable a firewall, reboot or remove packages without explicit reviewed variables.
- Package installation is allowlisted and profile-driven.
- Secrets are never committed to Git.
- Customer-specific values live outside the generic baseline.

## Acceptance

- Syntax checks and lint pass for every supported distribution profile.
- Idempotence demonstrated on a disposable VM per distribution.
- Hardware, browser, office, conferencing, printer and recovery tests pass.
- Re-run produces no unintended changes.
- Security update lifecycle and remote management are supportable.
