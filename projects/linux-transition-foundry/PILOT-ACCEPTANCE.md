# Pilot plan and acceptance criteria

## Pilot cohort

Select a small representative cohort (typically 3–5 users for an initial small-business pilot), with business-owner approval. Include a standard office user, a manager, a technically confident user, a user with printing/peripheral needs and, if relevant, a specialist application user.

## Entry criteria

- Discovery and application/workflow inventory approved.
- Critical workflows classified and owners assigned.
- Target hardware validated.
- Data backup completed and restore test passed.
- Identity, security, support and rollback design approved.
- User communication and training prepared.
- Pilot success measures and observation period agreed.

## Test matrix

| Area | Evidence required |
|---|---|
| Identity | Login, MFA, group access, lockout and offboarding tests |
| Documents | Representative files, templates, macros and export/import fidelity |
| Email/calendar | Mail, calendar, contacts, shared mailboxes and delegation as required |
| Collaboration | Calls, screen sharing, camera, microphone and file collaboration |
| Printing/scanning | Required models, duplex, trays, scan destinations and drivers |
| Network | Wi-Fi, VPN, DNS, proxy, SMB and remote access |
| Business apps | Owner-approved end-to-end workflow tests |
| Security | Encryption, firewall, least privilege, updates and endpoint controls |
| Backup | Successful restore of user data and configuration |
| Recovery | Rebuild or rollback rehearsal |
| Support | Helpdesk runbook and common incident exercises |
| Usability | User feedback and task completion compared with baseline |

## Acceptance gates

- 100% of critical workflows have a passed test or an explicitly approved Windows exception.
- No open critical or high-severity security defects.
- Backup restore and rollback have been demonstrated.
- Support team can provision, patch, diagnose and recover a pilot endpoint.
- Business owner signs off workflow equivalence or documented exceptions.
- User-impact measures meet thresholds agreed before pilot.
- Cost model updated with observed migration and support effort.

## Rollback

Retain the previous endpoint or recoverable image and user data until acceptance. Define a rollback trigger, decision owner, maximum decision time, data reconciliation procedure and communication plan. Never assume a reverse migration is lossless; test it.

## Evidence pack

Store redacted test results, configuration version, software bill of materials where applicable, exceptions, security findings, user feedback, recovery evidence and signed acceptance. Do not store passwords, private keys or unnecessary employee data.
