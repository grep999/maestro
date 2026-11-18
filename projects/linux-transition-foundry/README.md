# Linux Transition Foundry

A Maestro-managed project to move Windows-dependent users and organisations toward managed Linux while preserving their data and workflows.

## Product promise
Reduce avoidable IT cost and vendor dependency without sacrificing continuity, security, supportability or user productivity. We migrate workflows, not just operating systems.

## Initial wedge
Small organisations (10–50 endpoints) with browser, email, documents, file shares and standard office workflows. Specialist Windows-only workloads remain exceptions until validated replacements exist.

## Delivery model
1. Paid readiness assessment.
2. Verified data backup and workflow/application disposition.
3. Hardware-matched Linux distribution pilot.
4. Department-by-department migration.
5. Managed Linux operations and reusable tooling.

## Flexible distribution support
Ubuntu Desktop remains the standard profile for capable PCs, but older hardware can be matched to Linux Mint Xfce, Xubuntu, Lubuntu, MX Linux Xfce, Debian LXQt or antiX. A hardware-aware recommender screens RAM and CPU architecture. See DISTRIBUTION-MATRIX.md. It recommends candidates only; live hardware and workflow validation remain mandatory.

## Migration utility
The prototype in tools/ performs selected-folder Windows backup with a SHA-256 manifest and a verified, dry-run-first Ubuntu/Linux restore into a new directory. It never deletes source data or overwrites existing files. It is not an OS installer or complete application/profile migration product.

## Project status
Reference-design and prototype phase. No customer environment has been migrated. Backup/restore and distribution profiles require disposable-VM and hardware testing before pilot use.
