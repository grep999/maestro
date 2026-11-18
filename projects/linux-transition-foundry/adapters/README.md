# Distribution adapter contract

Status: contract and metadata only; no package or service mutation is implemented.

The migration engine owns customer intent, safety gates, backup/restore, acceptance and audit history. A distribution adapter translates an approved baseline into distribution-specific package and service operations. It must not decide whether migration is authorised.

## Contract boundary

An adapter receives the selected profile ID, runtime facts collected from the installed/live system, an allowlisted baseline intent, and an explicit operation policy and approval record.

It returns a plan before execution: detected distribution/version and architecture; package manager and exact package names; active PID 1/service manager; service names and supported operations; repository provenance and package availability; unsupported capabilities and blockers.

The engine reviews the plan and presents it for approval. No adapter may infer approval from profile selection.

## Profile versus running init

MX Linux can boot with systemd or SysVinit. antiX 26.1 includes runit, SysVinit, dinit, s6-rc and s6-66, with runit as default. Debian installations can use alternative init systems. Therefore MX, antiX and Debian must detect the running PID 1 rather than assume a service manager from the distro name.

For antiX, service package availability is init-specific. A package being available in APT does not prove that its service is installable or operable under the selected init.

## Current metadata

The JSON catalogue is a reviewed candidate catalogue. automation_status=candidate_only is deliberate: none of these profiles is production-approved. The catalogue is not proof that the named OS version, hardware, package or service is present.

## Safety rules

- Package operations are disabled by default and must be allowlisted.
- Service enable/disable/restart operations are disabled by default.
- Never replace init systems, switch init at boot, alter repositories, or upgrade a release as part of baseline convergence.
- Never run apt upgrade, dist-upgrade, autoremove or unattended package transactions in this migration phase.
- Unknown distribution, version, architecture, package manager or PID 1 blocks mutation.
- Package/service plans are generated and reviewed before any write.
- Every execution records exact command, package/service identifiers, exit code and before/after state.
- Idempotence and rollback must be demonstrated in disposable VMs for each profile before production support.

## Next implementation

1. Runtime fact collector for /etc/os-release, architecture, package-manager availability and /proc/1/comm without changing state.
2. Strict profile/runtime compatibility validator.
3. Read-only package availability planner.
4. Separate systemd, SysVinit and runit service adapters; other init systems remain blocked until independently tested.
5. Per-profile Ansible roles and VM acceptance matrix.

## Source notes

- antiX 26.1 release notes: https://antixlinux.com/category/releases/ (multi-init release, runit default, 32/64-bit flavours).
- antiX 26 FAQ: https://robin-antix.codeberg.page/antiX-FAQ/antiX26/init.html (available init systems and service-package implications).
- MX Linux 25 user manual: https://raw.githubusercontent.com/MX-Linux/mx-docs/master/mxum_en.pdf (systemd and SysVinit boot choices).
- Debian init reference: https://wiki.debian.org/Init (runtime init detection guidance and alternative init support).
- Ubuntu package management: https://ubuntu.com/server/docs/how-to/software/package-management/ (APT package management).
- Linux Mint release catalogue: https://www.linuxmint.com/download_all.php (22.3 Ubuntu Noble package base).
