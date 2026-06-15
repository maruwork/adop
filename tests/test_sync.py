"""Tests for adop_sync drift detection, apply, register, push, and list."""
from __future__ import annotations

import json

import pytest

import adop_sync


RUNTIME_NAMES = ["adop_types.py", "adop_cli.py"]


@pytest.fixture
def canon(tmp_path):
    root = tmp_path / "adop"
    root.mkdir()
    py = root / "shared" / "python"
    py.mkdir(parents=True)
    for name in RUNTIME_NAMES:
        (py / name).write_text(f"# {name} v2", encoding="utf-8")
    manifest = {
        "name": "adop", "version": "0.1.0",
        "canonical_repo": "https://github.com/maruwork/adop",
        "runtime_files": [f"shared/python/{n}" for n in RUNTIME_NAMES],
    }
    (root / "adop.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


@pytest.fixture
def copy_dir(tmp_path):
    d = tmp_path / "project_copy"
    d.mkdir()
    return d


def _populate_copy(copy_dir, content_map):
    for name, content in content_map.items():
        (copy_dir / name).write_text(content, encoding="utf-8")


# --- check ---

def test_check_all_ok(canon, copy_dir):
    _populate_copy(copy_dir, {n: f"# {n} v2" for n in RUNTIME_NAMES})
    assert adop_sync.cmd_check(canon, copy_dir) == 0


def test_check_detects_diff(canon, copy_dir):
    _populate_copy(copy_dir, {"adop_types.py": "# old", "adop_cli.py": "# adop_cli.py v2"})
    assert adop_sync.cmd_check(canon, copy_dir) == 1


def test_check_detects_missing_file(canon, copy_dir):
    _populate_copy(copy_dir, {"adop_types.py": "# adop_types.py v2"})
    # adop_cli.py absent
    assert adop_sync.cmd_check(canon, copy_dir) == 1


# --- apply ---

def test_apply_copies_diff(canon, copy_dir):
    _populate_copy(copy_dir, {n: "# old" for n in RUNTIME_NAMES})
    assert adop_sync.cmd_apply(canon, copy_dir) == 0
    assert (copy_dir / "adop_types.py").read_text() == "# adop_types.py v2"
    assert (copy_dir / "adop_cli.py").read_text() == "# adop_cli.py v2"


def test_apply_copies_missing(canon, copy_dir):
    _populate_copy(copy_dir, {"adop_types.py": "# adop_types.py v2"})
    assert adop_sync.cmd_apply(canon, copy_dir) == 0
    assert (copy_dir / "adop_cli.py").read_text() == "# adop_cli.py v2"


def test_apply_noop_when_ok(canon, copy_dir):
    _populate_copy(copy_dir, {n: f"# {n} v2" for n in RUNTIME_NAMES})
    assert adop_sync.cmd_apply(canon, copy_dir) == 0


# --- register + list ---

def test_register_adds_target(canon, copy_dir):
    adop_sync.cmd_register(canon, copy_dir)
    assert str(copy_dir.resolve()) in adop_sync._load_registry(canon)


def test_register_idempotent(canon, copy_dir):
    adop_sync.cmd_register(canon, copy_dir)
    adop_sync.cmd_register(canon, copy_dir)
    assert adop_sync._load_registry(canon).count(str(copy_dir.resolve())) == 1


def test_list_empty(canon, capsys):
    adop_sync.cmd_list(canon)
    assert "no registered targets" in capsys.readouterr().out


def test_list_shows_drift(canon, copy_dir, capsys):
    _populate_copy(copy_dir, {"adop_types.py": "# old", "adop_cli.py": "# old"})
    adop_sync.cmd_register(canon, copy_dir)
    adop_sync.cmd_list(canon)
    assert "DRIFT" in capsys.readouterr().out


# --- push ---

def test_push_updates_registered_target(canon, copy_dir):
    _populate_copy(copy_dir, {n: "# old" for n in RUNTIME_NAMES})
    adop_sync.cmd_register(canon, copy_dir)
    assert adop_sync.cmd_push(canon) == 0
    assert (copy_dir / "adop_types.py").read_text() == "# adop_types.py v2"


def test_push_empty_registry(canon):
    assert adop_sync.cmd_push(canon) == 0
