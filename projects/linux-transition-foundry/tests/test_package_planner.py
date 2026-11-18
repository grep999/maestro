import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "plan-office-packages.py"
SPEC = importlib.util.spec_from_file_location("plan_office_packages", MODULE)
planner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(planner)


class PackagePlannerTests(unittest.TestCase):
    def test_complete_snapshot_produces_reviewable_plan_without_mutations(self):
        available = {
            name: True
            for group in planner.CATALOG["ubuntu-desktop"].values()
            for name in group
        }
        report = planner.build_plan("ubuntu-desktop", available)
        self.assertEqual(report["status"], "READY_FOR_HUMAN_REVIEW")
        self.assertFalse(report["execution"]["mutations_permitted"])
        self.assertEqual(report["execution"]["packages_to_install"], [])
        self.assertEqual(len(report["groups"]), 4)

    def test_missing_snapshot_entries_fail_closed(self):
        report = planner.build_plan("ubuntu-desktop", {})
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(set(report["blockers"]), set(planner.CATEGORIES))
        self.assertTrue(all(c["availability"] == "unknown"
                            for g in report["groups"] for c in g["candidates"]))

    def test_unavailable_candidate_is_not_selected(self):
        report = planner.build_plan("ubuntu-desktop", {"firefox": False})
        browser = next(g for g in report["groups"] if g["category"] == "browser")
        self.assertIsNone(browser["selected"])
        self.assertEqual(browser["status"], "blocked")

    def test_first_available_candidate_is_selected_deterministically(self):
        report = planner.build_plan("mx-xfce", {
            "firefox-esr": True,
            "libreoffice-writer": True,
            "libreoffice-calc": True,
            "libreoffice-impress": True,
            "atril": True,
            "engrampa": True,
        })
        self.assertEqual(report["status"], "READY_FOR_HUMAN_REVIEW")
        self.assertEqual([g["selected"] for g in report["groups"]],
                         ["firefox-esr", "libreoffice-writer", "atril", "engrampa"])

    def test_unknown_profile_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown_profile"):
            planner.build_plan("unknown", {})

    def test_non_object_snapshot_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must_be_object"):
            planner.build_plan("ubuntu-desktop", [])

    def test_no_profile_can_authorize_execution(self):
        for profile in planner.CATALOG:
            report = planner.build_plan(profile, {})
            self.assertFalse(report["execution"]["mutations_permitted"])
            self.assertFalse(report["execution"]["network_accessed"])
            self.assertFalse(report["execution"]["privilege_required"])


if __name__ == "__main__":
    unittest.main()
