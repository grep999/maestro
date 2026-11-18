#!/usr/bin/env python3
"""Read-only Linux runtime discovery and fail-closed distro profile validation."""
import argparse
import json
import platform
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "adapters" / "distribution-adapters.json").read_text(encoding="utf-8"))
PROFILES = CONTRACT["profiles"]

PROFILE_OS_IDS = {
    "ubuntu-desktop": {"ubuntu"},
    "xubuntu": {"ubuntu"},
    "lubuntu": {"ubuntu"},
    "mint-xfce": {"linuxmint"},
    "mx-xfce": {"mx"},
    "debian-lxqt": {"debian"},
    "antix": {"antix"},
}
ARCH_ALIASES = {
    "x86_64": "x64", "amd64": "x64",
    "i386": "x86", "i486": "x86", "i586": "x86", "i686": "x86",
    "aarch64": "arm64", "arm64": "arm64",
    "armv7l": "armv7", "armv6l": "armv6",
}
PID1_ALIASES = {
    "systemd": "systemd",
    "init": "sysvinit",
    "runit": "runit",
    "dinit": "dinit",
    "s6-svscan": "s6-unknown",
    "s6-linux-init": "s6-unknown",
}

def parse_os_release(path):
    """Parse the simple KEY=VALUE format without sourcing or executing the file."""
    facts = {}
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return facts
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key and key.replace("_", "").isalnum():
            facts[key] = value
    return facts

def detect_pid1(path):
    try:
        raw = Path(path).read_text(encoding="utf-8").strip().split("/")[-1]
    except (OSError, UnicodeError):
        return "unknown"
    name = raw.lower()
    for token, manager in PID1_ALIASES.items():
        if name == token or name.startswith(token + "-"):
            return manager
    return "unknown"

def collect_runtime_facts(os_release_path="/etc/os-release", pid1_path="/proc/1/comm",
                          machine=None, which=shutil.which):
    release = parse_os_release(os_release_path)
    machine = (machine if machine is not None else platform.machine()).lower()
    architecture = ARCH_ALIASES.get(machine, "unknown")
    package_manager = "apt" if which("apt-get") or which("apt") else "unknown"
    return {
        "os_id": release.get("ID", "").lower(),
        "os_version_id": release.get("VERSION_ID", ""),
        "os_like": release.get("ID_LIKE", "").lower().split(),
        "architecture": architecture,
        "package_manager": package_manager,
        "pid1": detect_pid1(pid1_path),
    }

def validate_profile(profile_id, facts):
    """Return blockers; an empty list means only metadata compatibility, not device approval."""
    blockers = []
    profile = PROFILES.get(profile_id)
    if profile is None:
        return ["unknown_profile"]
    for key in ("os_id", "os_version_id", "architecture", "package_manager", "pid1"):
        if not facts.get(key) or facts[key] == "unknown":
            blockers.append("unknown_" + key)
    if facts.get("os_id") not in PROFILE_OS_IDS.get(profile_id, set()):
        blockers.append("distribution_id_mismatch")
    if facts.get("os_version_id") not in profile.get("supported_versions", []):
        blockers.append("unsupported_distribution_version")
    if facts.get("architecture") not in ("x64", "x86"):
        blockers.append("unsupported_architecture")
    if facts.get("architecture") not in profile.get("arch", ["x64"]):
        blockers.append("profile_architecture_mismatch")
    if facts.get("package_manager") != profile.get("package_manager"):
        blockers.append("package_manager_mismatch")
    expected_init = profile.get("service_manager")
    if expected_init != "runtime_detect" and facts.get("pid1") != expected_init:
        blockers.append("service_manager_mismatch")
    if expected_init == "runtime_detect":
        allowed = profile.get("observed_init_options", [])
        if facts.get("pid1") not in allowed:
            blockers.append("unsupported_service_manager")
    return sorted(set(blockers))

def build_report(profile_id, facts):
    blockers = validate_profile(profile_id, facts)
    return {
        "schema_version": 1,
        "profile_id": profile_id,
        "runtime": facts,
        "compatibility": "METADATA_COMPATIBLE" if not blockers else "BLOCKED",
        "blockers": blockers,
        "automation_status": PROFILES.get(profile_id, {}).get("automation_status", "unsupported"),
        "mutations_permitted": False,
        "reboot_permitted": False,
        "limitations": [
            "Read-only discovery; no package, service, repository, disk, bootloader or reboot operation is performed.",
            "Metadata compatibility is not proof of hardware, driver, application, security or workflow compatibility.",
            "Live-boot acceptance and explicit customer approval remain mandatory."
        ]
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=sorted(PROFILES))
    parser.add_argument("--os-release", type=Path, default=Path("/etc/os-release"))
    parser.add_argument("--pid1", type=Path, default=Path("/proc/1/comm"))
    args = parser.parse_args(argv)
    facts = collect_runtime_facts(args.os_release, args.pid1)
    report = build_report(args.profile, facts)
    print(json.dumps(report, indent=2))
    return 0 if report["compatibility"] == "METADATA_COMPATIBLE" else 2

if __name__ == "__main__":
    raise SystemExit(main())
