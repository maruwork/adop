#!/usr/bin/env python3
"""ADOP runtime copy drift detection and sync.

Run from the ADOP canonical root (the directory that contains adop.json).

Target layout: --target points to the project root; runtime files are
copied preserving their canonical relative path (e.g. shared/python/adop_cli.py
→ <target>/shared/python/adop_cli.py).

Commands:
  check     --source <adop-root> --target <project-root>
            Compare file hashes. Exit 0 = all OK, 1 = drift found.
  apply     --source <adop-root> --target <project-root>
            Copy differing/missing files from source to target.
  register  --target <project-root> [--source <adop-root>]
            Add a project root to the local registry.
  push      [--source <adop-root>]
            Run apply against every registered target.
  list      [--source <adop-root>]
            Show registered targets and their current sync status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

_REGISTRY_FILE = "sync-registry.json"
_MANIFEST_FILE = "adop.json"


def _file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load_manifest(source: Path) -> dict:
    path = source / _MANIFEST_FILE
    if not path.exists():
        sys.exit(f"error: {path} not found — run from the ADOP canonical root")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        sys.exit(f"error: {path} is not readable JSON: {exc}")


def _load_registry(source: Path) -> list[str]:
    reg = source / _REGISTRY_FILE
    if not reg.exists():
        return []
    try:
        return json.loads(reg.read_text(encoding="utf-8")).get("targets", [])
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        sys.exit(f"error: {reg} is not readable JSON: {exc}")


def _save_registry(source: Path, targets: list[str]) -> None:
    (source / _REGISTRY_FILE).write_text(
        json.dumps({"targets": targets}, indent=2), encoding="utf-8"
    )


def _managed_files(manifest: dict) -> list[str]:
    """Files sync must keep in step: runtime modules plus declared templates.

    Each entry must be a project-relative path with no '..' and no absolute root,
    so a hostile/clone manifest cannot make apply/push write outside --target.
    """
    files = list(manifest.get("runtime_files", [])) + list(manifest.get("template_files", []))
    for rel in files:
        norm = str(rel).replace("\\", "/")
        # Reject leading-slash/drive-relative ("/etc/passwd"), Windows drive
        # ("C:\\..."), and any "../" traversal. is_absolute() alone is not enough:
        # on Windows "/etc/passwd" is drive-relative, not absolute.
        if (
            norm.startswith("/")
            or PureWindowsPath(rel).drive
            or PurePosixPath(norm).is_absolute()
            or ".." in PurePosixPath(norm).parts
        ):
            sys.exit(f"error: manifest path must be project-relative without '..': {rel}")
    return files


def _check_one(source: Path, target: Path, manifest: dict) -> list[dict]:
    """Check each managed file; dst preserves the canonical relative path."""
    results = []
    for rel in _managed_files(manifest):
        src = source / rel
        dst = target / rel  # preserve full relative path (e.g. shared/python/adop_cli.py)
        if not src.exists():
            results.append({"file": rel, "status": "MISSING_IN_SOURCE"})
        elif not dst.exists():
            results.append({"file": rel, "status": "MISSING", "src": str(src), "dst": str(dst)})
        else:
            ok = _file_hash(src) == _file_hash(dst)
            results.append(
                {
                    "file": rel,
                    "status": "OK" if ok else "DIFF",
                    "src": str(src),
                    "dst": str(dst),
                }
            )
    return results


def _print_results(target: Path, results: list[dict]) -> None:
    ok_count = sum(1 for r in results if r["status"] == "OK")
    bad_count = len(results) - ok_count
    print(f"  target : {target}")
    print(f"  result : {ok_count} OK, {bad_count} need attention")
    for r in results:
        print(f"    {r['status']:<8}  {r['file']}")


def cmd_check(source: Path, target: Path) -> int:
    manifest = _load_manifest(source)
    results = _check_one(source, target, manifest)
    _print_results(target, results)
    return 0 if all(r["status"] == "OK" for r in results) else 1


def cmd_apply(source: Path, target: Path) -> int:
    manifest = _load_manifest(source)
    results = _check_one(source, target, manifest)
    missing_in_source = [r for r in results if r["status"] == "MISSING_IN_SOURCE"]
    if missing_in_source:
        for r in missing_in_source:
            print(f"  error: {r['file']} is missing in source — apply aborted")
        return 1
    copied = 0
    for r in results:
        if r["status"] in ("DIFF", "MISSING"):
            dst = Path(r["dst"])
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(r["src"], dst)
            print(f"  copied: {r['file']}")
            copied += 1
    print("  all files up to date" if copied == 0 else f"  {copied} file(s) updated")
    return 0


def cmd_register(source: Path, target: Path) -> int:
    targets = _load_registry(source)
    key = str(target.resolve())
    if key in targets:
        print(f"  already registered: {key}")
        return 0
    targets.append(key)
    _save_registry(source, targets)
    print(f"  registered: {key}")
    return 0


def cmd_push(source: Path) -> int:
    manifest = _load_manifest(source)
    targets = _load_registry(source)
    if not targets:
        print("  no registered targets")
        return 0
    for t in targets:
        target = Path(t)
        print(f"\n→ {target}")
        if not target.exists():
            print("  warning: directory not found, skipping")
            continue
        results = _check_one(source, target, manifest)
        copied = 0
        for r in results:
            if r["status"] in ("DIFF", "MISSING"):
                dst = Path(r["dst"])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(r["src"], dst)
                print(f"  copied: {r['file']}")
                copied += 1
        print("  all files up to date" if copied == 0 else f"  {copied} file(s) updated")
    return 0


def cmd_list(source: Path) -> int:
    manifest = _load_manifest(source)
    targets = _load_registry(source)
    if not targets:
        print("  no registered targets")
        return 0
    for t in targets:
        target = Path(t)
        if not target.exists():
            print(f"  MISSING_DIR  {t}")
            continue
        results = _check_one(source, target, manifest)
        bad = [r for r in results if r["status"] != "OK"]
        label = "OK" if not bad else f"DRIFT ({len(bad)} file(s))"
        print(f"  {label:<22}  {t}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="adop_sync",
        description="ADOP runtime copy drift detection and sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="command")

    def _src(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--source",
            default=".",
            metavar="DIR",
            help="ADOP canonical root containing adop.json (default: .)",
        )

    def _tgt(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--target",
            required=True,
            metavar="DIR",
            help="Project root (runtime files placed at <target>/shared/python/)",
        )

    p = sub.add_parser("check", help="compare hashes, report DIFF")
    _src(p)
    _tgt(p)

    p = sub.add_parser("apply", help="copy differing/missing files to target")
    _src(p)
    _tgt(p)

    p = sub.add_parser("register", help="add target to local registry")
    _src(p)
    _tgt(p)

    p = sub.add_parser("push", help="apply to all registered targets")
    _src(p)

    p = sub.add_parser("list", help="show registered targets and sync status")
    _src(p)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    source = Path(args.source).resolve()

    if args.command == "check":
        return cmd_check(source, Path(args.target).resolve())
    if args.command == "apply":
        return cmd_apply(source, Path(args.target).resolve())
    if args.command == "register":
        return cmd_register(source, Path(args.target).resolve())
    if args.command == "push":
        return cmd_push(source)
    if args.command == "list":
        return cmd_list(source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
