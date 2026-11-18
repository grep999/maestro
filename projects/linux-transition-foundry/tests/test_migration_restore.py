import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
MODULE = Path(__file__).resolve().parents[1] / "tools" / "restore-to-ubuntu.py"
SPEC = importlib.util.spec_from_file_location("restore", MODULE)
restore = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(restore)

class RestoreSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "backup"
        (self.root / "Documents").mkdir(parents=True)
        data = b"test data\n"
        (self.root / "Documents" / "note.txt").write_bytes(data)
        self.manifest = {"format":"linux-transition-foundry-backup","version":1,
            "files":[{"path":"Documents/note.txt","size":len(data),"sha256":hashlib.sha256(data).hexdigest()}]}
        (self.root / "migration-manifest.json").write_text(json.dumps(self.manifest))
    def tearDown(self): self.tmp.cleanup()
    def test_valid_manifest(self):
        self.assertEqual(len(restore.plan(self.root, Path(self.tmp.name)/"out", restore.load_manifest(self.root))), 1)
    def test_tamper_detected(self):
        (self.root/"Documents"/"note.txt").write_text("bad")
        with self.assertRaises(ValueError): restore.plan(self.root, Path(self.tmp.name)/"out", restore.load_manifest(self.root))
    def test_traversal_rejected(self):
        with self.assertRaises(ValueError): restore.safe_relative_path("../escape")
    def test_absolute_rejected(self):
        with self.assertRaises(ValueError): restore.safe_relative_path("/etc/passwd")
    def test_duplicate_rejected(self):
        self.manifest["files"].append(self.manifest["files"][0])
        (self.root/"migration-manifest.json").write_text(json.dumps(self.manifest))
        with self.assertRaises(ValueError): restore.plan(self.root, Path(self.tmp.name)/"out", restore.load_manifest(self.root))

if __name__ == "__main__": unittest.main()
