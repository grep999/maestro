# Linux Transition Foundry

A Maestro-managed project to move Windows-dependent users and organisations toward managed Linux while preserving their data and workflows.

## Product promise
Reduce avoidable IT cost and vendor dependency without sacrificing continuity, security, supportability or user productivity. We migrate workflows, not just operating systems.

## Initial wedge
Small organisations (10–50 endpoints) with browser, email, documents, file shares and standard office workflows. Specialist Windows-only workloads remain exceptions until validated replacements exist.

## Delivery model
1. Paid readiness assessment.
2. Verified data backup and workflow/application disposition.
3. Fixed-scope Ubuntu pilot.
4. Department-by-department migration.
5. Managed Linux operations and reusable tooling.

## Non-negotiable principles
- Evidence before recommendation; no assumed compatibility.
- No big-bang migrations.
- No device wipe before verified backup, acceptance and rollback readiness.
- Preserve required business workflows, not ideological OS purity.
- Least privilege, privacy by design and customer-approved discovery.
- Every deployment is reproducible, documented and recoverable.

## Migration utility
The prototype in tools/ performs a selected-folder Windows backup with SHA-256 manifest and a verified, dry-run-first Ubuntu restore into a new directory. It never deletes source data or overwrites existing files. See tools/README.md and MIGRATION-SAFETY.md. It is not an OS installer or a complete application/profile migration product.

## Project status
Reference-design and prototype phase. No customer environment has been migrated. Backup/restore tools still require disposable-VM testing, Windows-specific validation and independent security review before pilot use.
