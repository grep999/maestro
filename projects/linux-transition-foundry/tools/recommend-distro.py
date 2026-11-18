#!/usr/bin/env python3
"""Recommend a Linux desktop profile from a reviewed Windows inventory JSON."""
import argparse
import json
from pathlib import Path

PROFILES = {
    "ubuntu-desktop": {"name":"Ubuntu Desktop 26.04 LTS", "desktop":"GNOME", "ram_min_gb":6, "ram_comfort_gb":8, "arch":["x64"], "tier":"standard", "url":"https://ubuntu.com/download/desktop"},
    "xubuntu": {"name":"Xubuntu 26.04 LTS", "desktop":"Xfce", "ram_min_gb":2, "ram_comfort_gb":4, "arch":["x64"], "tier":"light", "url":"https://xubuntu.org/download/"},
    "lubuntu": {"name":"Lubuntu 26.04 LTS", "desktop":"LXQt", "ram_min_gb":2, "ram_comfort_gb":4, "arch":["x64"], "tier":"light", "url":"https://lubuntu.me/downloads/"},
    "mint-xfce": {"name":"Linux Mint 22.3 Xfce", "desktop":"Xfce", "ram_min_gb":2, "ram_comfort_gb":4, "arch":["x64"], "tier":"light", "url":"https://linuxmint.com/download.php"},
    "mx-xfce": {"name":"MX Linux 25 Xfce", "desktop":"Xfce", "ram_min_gb":1, "ram_comfort_gb":2, "arch":["x64"], "tier":"light", "url":"https://mxlinux.org/"},
    "debian-lxqt": {"name":"Debian 13 with LXQt", "desktop":"LXQt", "ram_min_gb":1, "ram_comfort_gb":2, "arch":["x64"], "tier":"light", "url":"https://www.debian.org/distrib/"},
    "antix": {"name":"antiX 26.1 Full", "desktop":"IceWM / window managers", "ram_min_gb":0.5, "ram_comfort_gb":1, "arch":["x64","x86"], "tier":"legacy", "url":"https://antixlinux.com/download/"},
}

def read_inventory(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    computer = data.get("computer") or {}
    processors = data.get("processors") or []
    os_data = data.get("operating_system") or {}
    ram = computer.get("TotalPhysicalMemory")
    if isinstance(ram, list):
        ram = ram[0] if ram else None
    if ram is None:
        memories = data.get("physical_memory") or []
        ram = sum(int(x.get("Capacity") or 0) for x in memories if isinstance(x, dict))
    if not ram:
        raise ValueError("Inventory has no usable physical RAM value.")
    cpu = processors[0] if processors and isinstance(processors[0], dict) else {}
    arch_text = str(os_data.get("OSArchitecture") or computer.get("SystemType") or "").lower()
    data_width = cpu.get("DataWidth")
    arch = "x86" if "32" in arch_text or data_width == 32 else "x64"
    return round(int(ram) / (1024 ** 3), 2), arch

def recommend(ram_gb, arch):
    if arch == "x86":
        choices = ["antix"] if ram_gb >= 0.5 else []
    elif ram_gb >= 6:
        choices = ["ubuntu-desktop", "mint-xfce", "xubuntu"]
    elif ram_gb >= 4:
        choices = ["mint-xfce", "xubuntu", "lubuntu"]
    elif ram_gb >= 2:
        choices = ["lubuntu", "xubuntu", "mint-xfce"]
    elif ram_gb >= 1:
        choices = ["mx-xfce", "debian-lxqt", "antix"]
    elif ram_gb >= 0.5:
        choices = ["antix"]
    else:
        choices = []
    return [{"id": key, **PROFILES[key]} for key in choices]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    ram, arch = read_inventory(args.inventory)
    choices = recommend(ram, arch)
    result = {"detected_ram_gb":ram, "architecture":arch, "recommendations":choices,
      "decision_note":"Hardware screening only. Boot each candidate in live mode and test Wi-Fi, graphics, suspend, audio, printers, encryption and required applications before choosing. These are recommendations, not compatibility guarantees.",
      "limitations":["Does not download ISOs or install an operating system.","Does not assess CPU instruction-set compatibility, GPU driver quality, Wi-Fi firmware or application compatibility.","Very low RAM may make modern browsers and office web apps impractical even when a distro boots."]}
    print(json.dumps(result, indent=2))
    return 0 if choices else 2

if __name__ == "__main__":
    raise SystemExit(main())
