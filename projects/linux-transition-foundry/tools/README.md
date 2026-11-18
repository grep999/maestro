# Migration and platform-selection tools

These tools support a cautious Windows-to-Linux transition. They do not install an operating system, repartition disks, migrate applications or credentials, or delete source data.

## 1. Windows backup
Use Start-WindowsDataBackup.ps1 to copy selected user folders to a separate encrypted external drive. Review the manifest and verify the backup independently before any OS installation.

## 2. Hardware inventory
Collect-WindowsInventory.ps1 gathers local hardware, processor architecture, OS, installed application and printer metadata. It is read-only. Review/redact its output before sharing.

## 3. Distribution recommendation
Run from the repository project directory:

~~~bash
python3 tools/recommend-distro.py path/to/reviewed-windows-inventory.json
~~~

The recommender screens physical RAM and CPU architecture against the curated profiles in DISTRIBUTION-MATRIX.md. It returns candidates, not a compatibility verdict. For 32-bit CPUs it only offers antiX; modern application availability must be checked separately.

## 4. Restore on Ubuntu or another supported Linux desktop
~~~bash
python3 tools/restore-to-ubuntu.py /media/$USER/DRIVE/Ubuntu-Migration-TIMESTAMP
python3 tools/restore-to-ubuntu.py /media/$USER/DRIVE/Ubuntu-Migration-TIMESTAMP --apply
~~~
First command verifies and previews. Second copies into ~/Migration-Import. Existing files are skipped, never overwritten. Use --target for a different destination.

## Platform selection rules
- 6 GB+ RAM: Ubuntu Desktop GNOME eligible.
- 4–6 GB: Linux Mint Xfce or Xubuntu preferred.
- 2–4 GB: Lubuntu or Xubuntu preferred.
- 1–2 GB: MX Linux Xfce or Debian LXQt; antiX for very constrained workloads.
- 512 MB–1 GB: antiX legacy exception only.
- Below 512 MB: no supported office recommendation.
- Always live-boot and test Wi-Fi, graphics, audio, suspend, peripherals, encryption, browser and required applications.

The RAM bands are conservative office-workload selection thresholds, not official installer minimums. See DISTRIBUTION-MATRIX.md for sources and limitations.

## Not automatically migrated
Windows applications/licences; email archives; browser profiles/passwords/passkeys/cookies; certificates/SSH keys; cloud-only files; WSL/VMs/databases/ERP/CAD state; Windows permissions, EFS, NTFS alternate streams and system settings. Export through supported application workflows and validate separately. Do not copy credential stores wholesale.

## Release gate
Prototype only. Test disposable Windows and Linux VMs with synthetic data. Validate interrupted copies, long paths, Unicode, OneDrive placeholders, reparse points, large data sets, each distro's hardware drivers and rollback. Independent security review is required before customer use.

## Distribution adapters

The adapters directory defines a candidate metadata contract, not executable provisioning. It deliberately distinguishes a distro profile from the init system actually running on the device. MX Linux and antiX support multiple init choices; Debian may also use alternatives. The engine must inspect runtime PID 1 before planning service operations. Package and service mutations, plus reboot, are disabled by default. See adapters/README.md. No profile is production-approved.

## Linux runtime discovery (read-only)

Run on a Linux live session or installed candidate:

~~~bash
python3 tools/discover-linux-runtime.py --profile ubuntu-desktop
~~~

Replace the profile with one of the IDs in adapters/distribution-adapters.json. The tool reads `/etc/os-release`, `platform.machine()` and `/proc/1/comm`, and checks for APT availability. It does not source shell files, invoke package managers, query the network, or modify the system. It returns a JSON compatibility report and exits non-zero when required facts are unknown or the distro ID, pinned version, architecture, package manager or active init do not match. A metadata-compatible result is not hardware or workflow approval, and it never authorises mutation.
