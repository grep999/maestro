from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANSIBLE = ROOT / "ansible"


class BaselineSafetyContract(unittest.TestCase):
    def test_firewall_is_opt_in(self):
        defaults = (ANSIBLE / "roles/office_baseline/defaults/main.yml").read_text()
        self.assertIn("baseline_manage_firewall: false", defaults)

    def test_inventory_is_empty_by_default(self):
        inventory = (ANSIBLE / "inventory/lab.yml").read_text()
        self.assertIn("hosts: {}", inventory)

    def test_no_destructive_or_remote_execution_modules(self):
        tasks = (ANSIBLE / "roles/office_baseline/tasks/main.yml").read_text()
        forbidden = (
            "ansible.builtin.shell:",
            "ansible.builtin.command:",
            "ansible.builtin.reboot:",
            "ansible.builtin.user:",
            "ansible.builtin.mount:",
            "community.general.parted:",
            "state: absent",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, tasks)

    def test_firewall_tasks_are_guarded(self):
        tasks = (ANSIBLE / "roles/office_baseline/tasks/main.yml").read_text()
        for block in tasks.split("- name: "):
            if "community.general.ufw:" in block:
                self.assertIn("when: baseline_manage_firewall | bool", block)

    def test_no_secrets_in_baseline_files(self):
        for path in ANSIBLE.rglob("*"):
            if path.is_file() and path.suffix in {".yml", ".yaml", ".cfg"}:
                content = path.read_text().lower()
                self.assertNotIn("password:", content)
                self.assertNotIn("private_key:", content)


if __name__ == "__main__":
    unittest.main()
