"""Tests for adop_sync drift detection, apply, register, push, and list.

Since Option B, --target is the project root and runtime files live at
<target>/shared/python/<name> (preserving the canonical relative path).
"""
from __future__ import annotations

import json
from pathlib import Path

import adop_sync
import pytest

RUNTIME_NAMES = ["adop_types.py", "adop_cli.py"]
RUNTIME_RELS = [f"shared/python/{n}" for n in RUNTIME_NAMES]


@pytest.fixture
def canon(tmp_path):
    root = tmp_path / "adop"
    root.mkdir()
    py = root / "shared" / "python"
    py.mkdir(parents=True)
    for name in RUNTIME_NAMES:
        (py / name).write_text(f"# {name} v2", encoding="utf-8")
    manifest = {
        "name": "adop", "version": "0.1.1",
        "canonical_repo": "https://github.com/maruwork/adop",
        "runtime_files": RUNTIME_RELS,
    }
    (root / "adop.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


@pytest.fixture
def project_root(tmp_path):
    """Simulated project root; runtime files live at project_root/shared/python/."""
    d = tmp_path / "myproject"
    d.mkdir()
    return d


def _populate(project_root: Path, content_map: dict[str, str]) -> None:
    """Write files under project_root/shared/python/ (structured layout)."""
    py = project_root / "shared" / "python"
    py.mkdir(parents=True, exist_ok=True)
    for name, content in content_map.items():
        (py / name).write_text(content, encoding="utf-8")


# --- check ---

def test_check_all_ok(canon, project_root):
    _populate(project_root, {n: f"# {n} v2" for n in RUNTIME_NAMES})
    assert adop_sync.cmd_check(canon, project_root) == 0


def test_check_detects_diff(canon, project_root):
    _populate(project_root, {"adop_types.py": "# old", "adop_cli.py": "# adop_cli.py v2"})
    assert adop_sync.cmd_check(canon, project_root) == 1


def test_check_detects_missing_file(canon, project_root):
    _populate(project_root, {"adop_types.py": "# adop_types.py v2"})
    # adop_cli.py absent
    assert adop_sync.cmd_check(canon, project_root) == 1


def test_check_structured_path_in_result(canon, project_root, capsys):
    """Result 'file' field uses the full relative path, not just the basename."""
    _populate(project_root, {"adop_types.py": "# old", "adop_cli.py": "# adop_cli.py v2"})
    adop_sync.cmd_check(canon, project_root)
    out = capsys.readouterr().out
    assert "shared/python/adop_types.py" in out


# --- apply ---

def test_apply_copies_diff(canon, project_root):
    _populate(project_root, {n: "# old" for n in RUNTIME_NAMES})
    assert adop_sync.cmd_apply(canon, project_root) == 0
    assert (project_root / "shared/python/adop_types.py").read_text() == "# adop_types.py v2"
    assert (project_root / "shared/python/adop_cli.py").read_text() == "# adop_cli.py v2"


def test_apply_copies_missing(canon, project_root):
    _populate(project_root, {"adop_types.py": "# adop_types.py v2"})
    assert adop_sync.cmd_apply(canon, project_root) == 0
    assert (project_root / "shared/python/adop_cli.py").read_text() == "# adop_cli.py v2"


def test_apply_creates_parent_dirs(canon, project_root):
    """apply must create shared/python/ if it does not exist."""
    assert adop_sync.cmd_apply(canon, project_root) == 0
    assert (project_root / "shared/python/adop_types.py").exists()


def test_apply_noop_when_ok(canon, project_root):
    _populate(project_root, {n: f"# {n} v2" for n in RUNTIME_NAMES})
    assert adop_sync.cmd_apply(canon, project_root) == 0


# --- register + list ---

def test_register_adds_target(canon, project_root):
    adop_sync.cmd_register(canon, project_root)
    assert str(project_root.resolve()) in adop_sync._load_registry(canon)


def test_register_idempotent(canon, project_root):
    adop_sync.cmd_register(canon, project_root)
    adop_sync.cmd_register(canon, project_root)
    assert adop_sync._load_registry(canon).count(str(project_root.resolve())) == 1


def test_list_empty(canon, capsys):
    adop_sync.cmd_list(canon)
    assert "no registered targets" in capsys.readouterr().out


def test_list_shows_drift(canon, project_root, capsys):
    _populate(project_root, {"adop_types.py": "# old", "adop_cli.py": "# old"})
    adop_sync.cmd_register(canon, project_root)
    adop_sync.cmd_list(canon)
    assert "DRIFT" in capsys.readouterr().out


# --- push ---

def test_push_updates_registered_target(canon, project_root):
    _populate(project_root, {n: "# old" for n in RUNTIME_NAMES})
    adop_sync.cmd_register(canon, project_root)
    assert adop_sync.cmd_push(canon) == 0
    assert (project_root / "shared/python/adop_types.py").read_text() == "# adop_types.py v2"


def test_push_empty_registry(canon):
    assert adop_sync.cmd_push(canon) == 0


# --- apply safety: MISSING_IN_SOURCE ---

def test_apply_aborts_when_source_file_missing(tmp_path, project_root):
    """apply must exit 1 when a manifest file is absent from the source."""
    # Build a canon whose manifest lists a file that does not exist in shared/python/
    root = tmp_path / "adop"
    root.mkdir()
    py = root / "shared" / "python"
    py.mkdir(parents=True)
    (py / "adop_types.py").write_text("# v2", encoding="utf-8")
    # adop_cli.py is declared in manifest but NOT written to disk
    manifest = {
        "name": "adop", "version": "0.1.1",
        "canonical_repo": "https://github.com/maruwork/adop",
        "runtime_files": ["shared/python/adop_types.py", "shared/python/adop_cli.py"],
    }
    (root / "adop.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert adop_sync.cmd_apply(root, project_root) == 1


def test_managed_files_rejects_escaping_path():
    import adop_sync
    import pytest
    with pytest.raises(SystemExit):
        adop_sync._managed_files({"runtime_files": ["../escape.py"], "template_files": []})


def test_managed_files_rejects_absolute_path():
    import adop_sync
    import pytest
    with pytest.raises(SystemExit):
        adop_sync._managed_files({"runtime_files": ["/etc/passwd"], "template_files": []})


def test_sync_clean_error_on_malformed_manifest(tmp_path):
    import adop_sync
    import pytest
    (tmp_path / "adop.json").write_text("{ not json", encoding="utf-8")
    with pytest.raises(SystemExit):
        adop_sync._load_manifest(tmp_path)
