# Migration methodology

## Phase 0 — Qualification and scope

Confirm business goals, endpoint count, locations, regulatory constraints, support expectations, budget, decision owner and acceptable change windows. Decline or defer projects where critical workflows cannot be validated or rollback cannot be assured.

## Phase 1 — Discovery

Collect only customer-authorised inventory:
- Hardware model, CPU architecture, RAM, storage, firmware and peripheral identifiers.
- Windows edition/build, encryption and management state.
- Installed applications and versions; usage evidence where available and approved.
- Identity, directory, authentication, network, VPN, Wi-Fi, printing and file services.
- Business workflows, integrations, macros, templates and data formats.
- Backup, recovery, endpoint protection, monitoring and support arrangements.
- Licensing obligations, vendor support terms and data residency requirements.

Do not collect personal files, browsing history, credentials or employee content as a default inventory practice.

Deliverables: asset register, application/workflow catalogue, dependency map, risk register and baseline TCO.

## Phase 2 — Compatibility and disposition

Classify each workflow, not merely each application:
- NATIVE: supported Linux application and validated workflow.
- WEB: supported browser workflow with feature parity accepted by owner.
- REPLACE: alternative selected and business owner accepts differences.
- ADAPT: integration, conversion, plugin or workflow change required.
- WINDOWS_EXCEPTION: retain Windows through managed endpoint, VDI/RDS or dedicated device.
- BLOCKER: no acceptable solution or risk remains.

Record evidence, owner, test date, vendor support status, data compatibility, licensing and rollback for every critical workflow. WINE is not a default production strategy for business-critical applications.

## Phase 3 — Target architecture and business case

Select distribution and management model based on hardware lifecycle, support, security maintenance, fleet tooling, skills and application requirements. Define identity, endpoint management, patching, encryption, software supply chain, backup, monitoring, remote support and exception handling.

Compare current and proposed 3–5 year TCO using equivalent service levels. Include migration labour, training, coexistence, application subscriptions, support, hardware replacement, downtime risk and Windows exceptions. Present assumptions and sensitivity ranges; do not promise savings before measurement.

## Phase 4 — Build reference baseline

Create version-controlled, reproducible configuration. Automate provisioning and policy enforcement. Include endpoint hardening, disk encryption, firewall, identity integration, approved software, logging, backup, monitoring and recovery. Pin versions and document update channels.

## Phase 5 — Pilot

Choose a representative, volunteer group covering ordinary and specialised workflows. Run real work for an agreed observation period. Test login, MFA, office documents, macros, printing/scanning, conferencing, VPN, peripherals, file access, backups, updates, support and accessibility.

Acceptance requires signed workflow test results, no unresolved critical defects, tested recovery, trained support staff and user/business-owner approval.

## Phase 6 — Progressive rollout

Migrate in small department-based waves. For each wave: readiness check, verified backup, user communication, deployment, acceptance, hypercare and formal rollback decision. Keep the previous environment recoverable until acceptance and retention obligations are met.

## Phase 7 — Operate and improve

Operate patching, vulnerability response, software lifecycle, asset inventory, monitoring, backup restore tests, incident response and upstream compatibility. Review exceptions quarterly and reassess TCO annually.

## Stop conditions

Stop rollout if critical workflow failure, data integrity issue, security control regression, unacceptable user productivity impact, failed recovery test or unapproved scope change occurs.
