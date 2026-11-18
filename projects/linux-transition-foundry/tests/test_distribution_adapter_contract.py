import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "adapters" / "distribution-adapters.json").read_text())

class DistributionAdapterContractTests(unittest.TestCase):
    def test_every_recommender_profile_has_an_adapter_record(self):
        module_path = ROOT / "tools" / "recommend-distro.py"
        namespace = {"__name__": "adapter_test"}
        exec(compile(module_path.read_text(), str(module_path), "exec"), namespace)
        self.assertEqual(set(namespace["PROFILES"]), set(CONTRACT["profiles"]))

    def test_all_profiles_are_candidate_only(self):
        self.assertTrue(all(p["automation_status"] == "candidate_only" for p in CONTRACT["profiles"].values()))

    def test_mutations_are_disabled_by_default(self):
        policy = CONTRACT["policy"]
        self.assertFalse(policy["package_changes_default"])
        self.assertFalse(policy["service_changes_default"])
        self.assertFalse(policy["reboot_default"])

    def test_multi_init_distributions_require_runtime_detection(self):
        for profile_id in ("mx-xfce", "debian-lxqt", "antix"):
            profile = CONTRACT["profiles"][profile_id]
            self.assertEqual(profile["service_manager"], "runtime_detect")
            self.assertGreaterEqual(len(profile["observed_init_options"]), 2)

    def test_antix_declares_all_documented_init_families(self):
        supported = set(CONTRACT["profiles"]["antix"]["observed_init_options"])
        self.assertEqual(supported, {"runit", "sysvinit", "dinit", "s6-rc", "s6-66"})

    def test_runtime_facts_are_mandatory(self):
        required = set(CONTRACT["runtime_detection"]["required_facts"])
        self.assertTrue({"os_id", "os_version_id", "architecture", "package_manager", "pid1"} <= required)

if __name__ == "__main__":
    unittest.main()
