# Implementation status — Linux baseline, migration and distro selection

## Delivered
- Windows inventory helper, including WMI processor architecture code and data width for conservative x86/x64 screening.
- Hardware-aware Linux distribution recommender based on RAM and CPU architecture; unknown and non-x86 architectures fail closed with no recommendation.
- Curated profiles: Ubuntu Desktop 26.04 LTS, Linux Mint 22.3 Xfce, Xubuntu 26.04 LTS, Lubuntu 26.04 LTS, MX Linux 25 Xfce, Debian 13 LXQt and antiX 26.1.
- Windows user-data backup prototype with SHA-256 manifest.
- Linux restore utility with manifest verification, dry-run default, path/symlink safety, collision skipping and no source deletion.
- Distribution matrix, safety contract and unit tests.
- Existing Ansible baseline remains Ubuntu-specific; cross-distribution configuration roles are not yet implemented.

## Selection policy
Ubuntu GNOME remains the standard candidate for capable PCs. Xfce/LXQt distributions target lower-resource systems; antiX is a legacy exception for very old or 32-bit hardware. RAM thresholds are conservative office-workload policy thresholds, not vendor installer minima. The recommender screens only RAM and architecture; it cannot guarantee driver, application or peripheral compatibility.

## CI evidence from previous increment
- Python unittest discovery: 10/10 passed.
- Ansible collection installation and playbook syntax check: passed.
- Maestro validation: passed.
- Copilot review request failed with HTTP 422 due to licence/policy eligibility; no independent Copilot review was completed.

## Validation still pending for this increment
- Distro recommender tests on CI after architecture hardening.
- Windows inventory output against real Windows systems, including ARM64 and legacy WMI variants.
- Windows-to-Linux end-to-end backup/restore round trip.
- Disposable VM/live-boot tests for every curated distro.
- CPU instruction-set, GPU, Wi-Fi, Bluetooth, suspend, printing and encryption compatibility.
- Cross-distro Ansible roles and package/service maps.
- Independent security review and customer pilot.

## Release gate
No production migration until backup integrity, rollback, distro support lifecycle, hardware and application acceptance are demonstrated on the target device. Do not treat a RAM-based recommendation as proof of compatibility.
