import importlib.util
from pathlib import Path
import tempfile, json, unittest
MODULE=Path(__file__).resolve().parents[1]/"tools"/"recommend-distro.py"
SPEC=importlib.util.spec_from_file_location("recommend_distro",MODULE)
advisor=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(advisor)

class DistroRecommendationTests(unittest.TestCase):
    def test_modern_machine_prefers_standard_desktop(self):
        self.assertEqual(advisor.recommend(8,"x64")[0]["id"],"ubuntu-desktop")
    def test_midrange_machine_gets_xfce_options(self):
        ids=[x["id"] for x in advisor.recommend(4,"x64")]
        self.assertIn("mint-xfce",ids); self.assertIn("xubuntu",ids)
    def test_low_ram_machine_gets_lightweight_options(self):
        ids=[x["id"] for x in advisor.recommend(1.5,"x64")]
        self.assertIn("mx-xfce",ids); self.assertNotIn("ubuntu-desktop",ids)
    def test_32_bit_machine_is_restricted_to_antix_profile(self):
        self.assertEqual([x["id"] for x in advisor.recommend(2,"x86")],["antix"])
    def test_extremely_low_ram_is_flagged_no_match(self):
        self.assertEqual(advisor.recommend(0.25,"x86"),[])

if __name__=="__main__": unittest.main()
