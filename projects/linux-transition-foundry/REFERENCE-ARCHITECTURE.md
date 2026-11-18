# Reference architecture — candidate baseline

This is a starting reference, not a universal prescription. Final choices require a discovery report and pilot evidence.

## Workstation layer

- Candidate desktop: Ubuntu LTS with GNOME for standard office endpoints.
- Alternatives: Debian stable or an enterprise-supported distribution where lifecycle, hardware, support or policy requirements justify it.
- Full-disk encryption using LUKS where supported and operationally manageable.
- Secure Boot and firmware configuration validated per hardware model.
- AppArmor, host firewall, least-privilege users and controlled administrative elevation.
- Supported browser and approved application catalogue.

## Identity and access

- Integrate with existing identity where feasible; validate AD/LDAP, Kerberos, SSSD, group mapping, MFA and lifecycle behaviour.
- Do not assume Windows Group Policy maps directly to Linux policy.
- Define local break-glass access, credential rotation and offboarding.
- Prefer central identity and device posture controls with documented failure modes.

## Fleet management

- Ansible for configuration management and repeatable setup.
- Inventory and endpoint telemetry selected according to privacy, scale and operational needs (osquery/Fleet are candidates).
- Managed package sources, staged updates and rollback strategy.
- Device enrolment, configuration drift detection and lifecycle reporting.

## Applications and data

- Prefer supported native applications and web services.
- Validate document fidelity, macros, fonts, templates, add-ins and collaboration workflows.
- Preserve Windows exceptions using managed Windows endpoints or remote application infrastructure where necessary.
- File services may use existing SMB infrastructure; test permissions, locking, offline use and identity mapping.

## Operations

- Monitoring: Prometheus/Grafana are candidate components where justified.
- Backup: Restic or Borg are candidates; separately test restore, retention and immutable/off-site requirements.
- Remote support: authenticated, logged and customer-approved tooling.
- Software supply chain: signed repositories, package provenance, SBOM where appropriate and vulnerability tracking.
- Configuration and documentation stored in version control with secrets kept in an approved secret manager.

## Security baseline

- Threat model and data classification.
- Secure boot/firmware checks, encryption, firewall and endpoint protection.
- Timely security updates and defined patch SLAs.
- Central logs with retention and access controls.
- Least privilege, MFA and account lifecycle.
- Tested backup restoration and incident response.
- Exceptions have named owners, compensating controls and expiry/review dates.

## Design decisions to record

For every customer: distribution/version, support lifecycle, hardware compatibility, identity method, management plane, package sources, application strategy, Windows exception design, backup, monitoring, patch rings, recovery objectives and data protection obligations.
