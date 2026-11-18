# Distribution support matrix (candidate policy)

This is a curated compatibility catalogue, not a promise that every device works. RAM figures in the advisor are conservative selection thresholds for a usable office workload, not installer minimums. Verify release lifecycle and hardware compatibility at each engagement.

| Profile | Desktop | Advisor RAM threshold | Best fit | Operational position |
|---|---|---:|---|---|
| Ubuntu Desktop 26.04 LTS | GNOME | 6 GB | Newer office PCs | Default standard profile |
| Linux Mint 22.3 Xfce | Xfce | 2 GB; 4 GB comfortable | Familiar desktop on modest x64 PCs | Preferred general-purpose lightweight option |
| Xubuntu 26.04 LTS | Xfce | 2 GB; 4 GB comfortable | Modest PCs needing Ubuntu ecosystem | Preferred Ubuntu-family lightweight option |
| Lubuntu 26.04 LTS | LXQt | 2 GB; 4 GB comfortable | Lower-resource x64 PCs | Lightweight Ubuntu-family option |
| MX Linux 25 Xfce | Xfce | 1 GB; 2 GB comfortable | Older x64 PCs | Alternative Debian-based profile; validate fleet-management integration |
| Debian 13 + LXQt | LXQt | 1 GB; 2 GB comfortable | Stable, configurable low-resource systems | Advanced/support-led profile |
| antiX 26.1 Full | IceWM and other window managers | 0.5 GB; 1 GB comfortable | Very old hardware, including supported 32-bit cases | Legacy exception; browser/modern web workloads may be impractical |

## Selection rules

- 6 GB+ RAM: Ubuntu GNOME is eligible; compare Mint Xfce/Xubuntu where lower overhead is useful.
- 4–6 GB: prefer Mint Xfce or Xubuntu; Lubuntu is also eligible.
- 2–4 GB: prefer Lubuntu or Xubuntu; test Mint Xfce against the actual workload.
- 1–2 GB: MX Xfce or Debian LXQt; antiX only where legacy hardware requires it and user workload is modest.
- 512 MB–1 GB: antiX is a legacy candidate, not a modern office guarantee. Assess whether replacement hardware is more economical.
- 32-bit x86: only antiX is currently included in this curated profile set. Confirm every required application has a maintained 32-bit build before proceeding.
- Below 512 MB: no supported office recommendation; advise hardware replacement or a narrowly scoped single-purpose use case.

## Common acceptance gates for every distribution

1. Boot live media before installation.
2. Verify CPU architecture and required instruction sets; RAM alone is insufficient.
3. Test Wi-Fi/Ethernet, GPU/display, audio, suspend/resume, Bluetooth, webcam, printer/scanner and docking.
4. Test disk health, SMART, firmware, UEFI/Secure Boot and encryption recovery.
5. Test real browser, office, conferencing and customer-specific applications under realistic memory pressure.
6. Confirm security-update lifecycle, repository trust, remote management and backup/restore integration.
7. Record the exact ISO checksum, release, kernel, desktop and hardware model.

## Source notes (official project documentation)

- Ubuntu Desktop 26.04: 6 GB minimum, 2 GHz dual-core and 25 GB free storage; official documentation recommends Ubuntu flavours such as Xubuntu/Lubuntu for systems with 2 GB RAM or more. https://documentation.ubuntu.com/release-notes/26.04/
- Xubuntu 26.04.1 desktop image: at least 1024 MiB to install. https://cdimage.ubuntu.com/xubuntu/releases/26.04/release/
- Lubuntu 26.04.1 LTS is available; support through April 2029. https://lubuntu.me/downloads/
- Linux Mint 22.3: 2 GB RAM, 4 GB recommended, support through 2029; Xfce edition is explicitly the lighter desktop option. https://blog.linuxmint.com/?p=4981 and https://linuxmint.com/download.php
- antiX 26.1: project states 512 MB recommended minimum and 7 GB disk minimum; 32-bit and 64-bit full images are offered. https://antixlinux.com/about/ and https://antixlinux.com/download/
- Debian 13 installation guide: desktop install 1 GB minimum / 2 GB recommended and 10 GB disk in its generic requirements table. https://www.debian.org/releases/stable/amd64/install.en.pdf
- MX Linux 25 installation manual: 1 GB RAM minimum for hard-disk installation; verify the current manual and release at deployment. https://mxlinux.org/
