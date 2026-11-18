#!/usr/bin/env python3
"""Verify and safely restore a Windows user-data backup into a new Ubuntu folder."""
import argparse, hashlib, json, shutil, sys
from pathlib import Path, PurePosixPath

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def safe_relative_path(raw):
    p = PurePosixPath(raw)
    if p.is_absolute() or not p.parts or any(x in ("", ".", "..") for x in p.parts) or "\\" in raw or "\x00" in raw:
        raise ValueError(f"Unsafe manifest path: {raw!r}")
    return Path(*p.parts)

def load_manifest(root):
    data = json.loads((root / "migration-manifest.json").read_text(encoding="utf-8-sig"))
    if data.get("format") != "linux-transition-foundry-backup" or data.get("version") != 1 or not isinstance(data.get("files"), list):
        raise ValueError("Unsupported or invalid migration manifest.")
    return data

def plan(root, target, manifest):
    operations, seen = [], set()
    for entry in manifest["files"]:
        rel = safe_relative_path(entry["path"])
        if rel.as_posix() == "migration-manifest.json" or rel in seen:
            raise ValueError(f"Duplicate or reserved manifest path: {rel}")
        seen.add(rel)
        src = root / rel
        cursor = root
        for part in rel.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError(f"Symlink in backup path: {rel}")
        if not src.is_file():
            raise ValueError(f"Backup file missing or not regular: {rel}")
        if root not in src.resolve().parents:
            raise ValueError(f"Backup path escapes source root: {rel}")
        if src.stat().st_size != int(entry["size"]) or sha256(src) != entry["sha256"]:
            raise ValueError(f"Size or SHA-256 mismatch: {rel}")
        operations.append((src, target / rel))
    return operations

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("backup", type=Path)
    ap.add_argument("--target", type=Path, default=Path.home() / "Migration-Import")
    ap.add_argument("--apply", action="store_true", help="Copy files; default is verification and preview only")
    args = ap.parse_args()
    root, target = args.backup.expanduser().resolve(), args.target.expanduser()
    if not root.is_dir():
        ap.error("Backup folder does not exist.")
    ops = plan(root, target, load_manifest(root))
    print(f"Backup verified: {len(ops)} files. Destination: {target}")
    if not args.apply:
        print("DRY RUN ONLY. Re-run with --apply to copy.")
        return 0
    target.mkdir(parents=True, exist_ok=True)
    base = target.resolve()
    copied = skipped = 0
    for src, dst in ops:
        dst.parent.mkdir(parents=True, exist_ok=True)
        parent = dst.parent.resolve()
        if parent != base and base not in parent.parents:
            raise ValueError(f"Destination escapes restore root: {dst}")
        if dst.exists():
            skipped += 1
            print(f"SKIP existing: {dst}")
            continue
        shutil.copy2(src, dst)
        if sha256(dst) != sha256(src):
            dst.unlink(missing_ok=True)
            raise IOError(f"Post-copy verification failed: {dst}")
        copied += 1
    print(f"Restore complete: {copied} copied, {skipped} existing skipped. Source backup unchanged.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
