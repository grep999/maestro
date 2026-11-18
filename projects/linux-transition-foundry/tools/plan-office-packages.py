#!/usr/bin/env python3
"""Build a deterministic, read-only office package plan from supplied APT metadata.

This module never invokes apt, accesses the network, changes package state, or runs
privileged commands. Callers provide a snapshot of package availability explicitly.
"""
import argparse
import json
from pathlib import Path

CATALOG = {
    "ubuntu-desktop": {
        "browser": ["firefox"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["evince"],
        "archive": ["file-roller"],
    },
    "xubuntu": {
        "browser": ["firefox"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["evince"],
        "archive": ["xarchiver"],
    },
    "lubuntu": {
        "browser": ["firefox"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["qpdfview"],
        "archive": ["xarchiver"],
    },
    "mint-xfce": {
        "browser": ["firefox"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["xreader"],
        "archive": ["engrampa"],
    },
    "mx-xfce": {
        "browser": ["firefox-esr"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["atril"],
        "archive": ["engrampa"],
    },
    "debian-lxqt": {
        "browser": ["firefox-esr"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["qpdfview"],
        "archive": ["xarchiver"],
    },
    "antix": {
        "browser": ["firefox-esr"],
        "office": ["libreoffice-writer", "libreoffice-calc", "libreoffice-impress"],
        "pdf": ["xpdf"],
        "archive": ["xarchiver"],
    },
}
CATEGORIES = ("browser", "office", "pdf", "archive")


def build_plan(profile_id, available_packages):
    """Return proposed package names and evidence; unknown availability fails closed."""
    if profile_id not in CATALOG:
        raise ValueError("unknown_profile")
    if not isinstance(available_packages, dict):
        raise ValueError("available_packages_must_be_object")

    groups = []
    for category in CATEGORIES:
        candidates = CATALOG[profile_id][category]
        states = []
        for name in candidates:
            value = available_packages.get(name)
            if value is True:
                state = "available"
            elif value is False:
                state = "unavailable"
            else:
                state = "unknown"
            states.append({"package": name, "availability": state})
        chosen = next((item["package"] for item in states
                       if item["availability"] == "available"), None)
        groups.append({
            "category": category,
            "candidates": states,
            "selected": chosen,
            "status": "planned" if chosen else "blocked",
        })

    blockers = [group["category"] for group in groups if group["selected"] is None]
    return {
        "schema_version": 1,
        "profile_id": profile_id,
        "groups": groups,
        "status": "READY_FOR_HUMAN_REVIEW" if not blockers else "BLOCKED",
        "blockers": blockers,
        "execution": {
            "packages_to_install": [],
            "mutations_permitted": False,
            "network_accessed": False,
            "privilege_required": False,
            "source_of_availability": "caller_supplied_snapshot",
        },
        "limitations": [
            "A supplied availability snapshot may be stale or incomplete.",
            "Availability does not prove package suitability, security, licence compliance or runtime compatibility.",
            "No package manager, network, repository, service or filesystem mutation is performed.",
            "A human must review the plan and obtain explicit approval before any future installation workflow."
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, choices=sorted(CATALOG))
    parser.add_argument("--availability", required=True, type=Path,
                        help="JSON object mapping package names to true/false")
    args = parser.parse_args(argv)
    snapshot = json.loads(args.availability.read_text(encoding="utf-8"))
    print(json.dumps(build_plan(args.profile, snapshot), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
