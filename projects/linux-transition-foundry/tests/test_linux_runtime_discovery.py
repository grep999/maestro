import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "discover-linux-runtime.py"
SPEC = importlib.util.spec_from_file_location("discover_linux_runtime", MODULE)
discovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(discovery)

class RuntimeDiscoveryTests(unittest.TestCase):
    def make_runtime(self, os_text='ID=ubuntu\nVERSION_ID="26.04"\n', pid1="systemd\n", machine="x86_64"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        os_file, pid_file = root / "os-release", root / "comm"
        os_file.write_text(os_text)
        pid_file.write_text(pid1)
        facts = discovery.collect_runtime_facts(os_file, pid_file, machine, which=lambda name: "/usr/bin/apt-get" if name == "apt-get" else None)
        return facts

    def test_ubuntu_systemd_is_metadata_compatible(self):
        facts = self.make_runtime()
        self.assertEqual(discovery.validate_profile("ubuntu-desktop", facts), [])
        report = discovery.build_report("ubuntu-desktop", facts)
        self.assertFalse(report["mutations_permitted"])
        self.assertFalse(report["reboot_permitted"])

    def test_mint_requires_its_own_distribution_id(self):
        facts = self.make_runtime("ID=ubuntu\nVERSION_ID=24.04\n")
        self.assertIn("distribution_id_mismatch", discovery.validate_profile("mint-xfce", facts))

    def test_mx_detects_sysvinit_from_pid1(self):
        facts = self.make_runtime("ID=mx\nVERSION_ID=25\n", "init\n")
        self.assertEqual(facts["pid1"], "sysvinit")
        self.assertEqual(discovery.validate_profile("mx-xfce", facts), [])

    def test_antix_runit_is_supported_but_unknown_init_blocks(self):
        facts = self.make_runtime("ID=antix\nVERSION_ID=26.1\n", "runit\n")
        self.assertEqual(discovery.validate_profile("antix", facts), [])
        facts["pid1"] = "mystery-init"
        self.assertIn("unsupported_service_manager", discovery.validate_profile("antix", facts))

    def test_unknown_runtime_facts_fail_closed(self):
        facts = {"os_id":"", "os_version_id":"", "architecture":"unknown",
                 "package_manager":"unknown", "pid1":"unknown"}
        blockers = discovery.validate_profile("ubuntu-desktop", facts)
        self.assertIn("unknown_os_id", blockers)
        self.assertIn("unknown_pid1", blockers)
        self.assertIn("unsupported_architecture", blockers)

    def test_arm64_is_reported_but_not_approved_by_current_profiles(self):
        facts = self.make_runtime(machine="aarch64")
        self.assertEqual(facts["architecture"], "arm64")
        self.assertIn("unsupported_architecture", discovery.validate_profile("ubuntu-desktop", facts))

    def test_os_release_is_parsed_as_data_not_executed(self):
        facts = self.make_runtime('ID=ubuntu\nVERSION_ID=26.04\nEVIL=$(touch /tmp/should-not-exist)\n')
        self.assertNotIn("EVIL", facts)

    def test_profile_never_enables_mutations(self):
        facts = self.make_runtime()
        for profile_id in discovery.PROFILES:
            report = discovery.build_report(profile_id, facts)
            self.assertFalse(report["mutations_permitted"])
            self.assertFalse(report["reboot_permitted"])

if __name__ == "__main__":
    unittest.main()
