"""Tests for tool-to-file coupling (entanglement) recording and reporting.

Covers the coupling-note artifact, the `couple` create command, the `couplings`
report, validation of the coupling vocabulary, snapshot (latest-wins) semantics,
and the summary "Tool Entanglement" section.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import adop_summary
from adop_validation import AdopValidationError, validate_coupling_note_payload

COUPLING_NOTE = "coupling-note"


def _summary(root: str, **kwargs) -> str:
    return adop_summary.build_summary(Path(root), **kwargs)


# --- create + report -------------------------------------------------------

def test_couple_records_full_snapshot(run, root, latest):
    code = run(
        "couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
        "--couple", "pyproject.toml|config|edit|ruff config",
        "--couple", "ci.yml|invocation|clean",
    )
    assert code == 0
    note = latest(root, COUPLING_NOTE, scene="lint")
    assert note["artifact_id"].startswith("cp-")
    assert note["candidate_or_tool"] == "ruff"
    assert len(note["couplings"]) == 2
    assert note["couplings"][0] == {
        "path": "pyproject.toml", "coupling_type": "config",
        "removal_cost": "edit", "note": "ruff config",
    }


def test_couplings_report_headline_is_worst_removal_cost(run, root, capsys):
    run("couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
        "--couple", "ci.yml|invocation|clean",
        "--couple", "src/legacy.py|reference|entangled")
    capsys.readouterr()
    code = run("couplings", "--artifact-root", root)
    assert code == 0
    out = capsys.readouterr().out
    # worst cost across files (clean, entangled) -> entangled
    assert "detachment: entangled" in out
    assert "ci.yml [invocation, clean]" in out


def test_couplings_json_report(run, root, capsys):
    run("couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
        "--couple", "pyproject.toml|config|edit")
    capsys.readouterr()
    run("couplings", "--artifact-root", root, "--json")
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 1
    entry = payload["report"][0]
    assert entry["tool"] == "ruff"
    assert entry["scene"] == "lint"
    assert entry["max_removal_cost"] == "edit"
    assert entry["file_count"] == 1


def test_couple_via_json_input(run, root, latest):
    couplings = json.dumps([
        {"path": "Makefile", "coupling_type": "invocation", "removal_cost": "clean"},
    ])
    code = run("couple", "--artifact-root", root, "--use-case", "build", "--tool", "make",
               "--couplings-json", couplings)
    assert code == 0
    note = latest(root, COUPLING_NOTE, scene="build")
    assert note["couplings"][0]["path"] == "Makefile"


# --- snapshot semantics ----------------------------------------------------

def test_latest_coupling_note_wins(run, root, capsys):
    """Each couple call is a full snapshot; the report uses only the latest."""
    run("couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
        "--couple", "a.py|reference|edit", "--couple", "b.py|reference|edit")
    run("couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
        "--couple", "a.py|reference|clean")  # decoupled b.py, a.py now clean
    capsys.readouterr()
    run("couplings", "--artifact-root", root)
    out = capsys.readouterr().out
    assert "1 file(s), detachment: clean" in out
    assert "b.py" not in out


def test_couplings_empty_report(run, root, capsys):
    capsys.readouterr()
    code = run("couplings", "--artifact-root", root)
    assert code == 0
    assert "no couplings recorded" in capsys.readouterr().out


# --- validation ------------------------------------------------------------

def test_validate_rejects_empty_couplings():
    with pytest.raises(AdopValidationError):
        validate_coupling_note_payload({
            "related_scene": "lint", "candidate_or_tool": "ruff", "couplings": [],
        })


def test_validate_rejects_bad_coupling_type():
    with pytest.raises(AdopValidationError):
        validate_coupling_note_payload({
            "related_scene": "lint", "candidate_or_tool": "ruff",
            "couplings": [{"path": "x", "coupling_type": "bogus", "removal_cost": "edit"}],
        })


def test_validate_rejects_bad_removal_cost():
    with pytest.raises(AdopValidationError):
        validate_coupling_note_payload({
            "related_scene": "lint", "candidate_or_tool": "ruff",
            "couplings": [{"path": "x", "coupling_type": "config", "removal_cost": "bogus"}],
        })


def test_validate_accepts_detection_metadata():
    validate_coupling_note_payload({
        "related_scene": "lint",
        "candidate_or_tool": "ruff",
        "couplings": [{
            "path": "pyproject.toml",
            "coupling_type": "config",
            "removal_cost": "edit",
            "detection_source": "surface-rule",
            "confidence": "high",
        }],
    })


def test_bad_couple_flag_format_returns_validation_error(run, root):
    code = run("couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
               "--couple", "missing-fields")
    assert code == 2  # PATH|TYPE|COST required


# --- summary integration ---------------------------------------------------

def test_summary_tool_entanglement_section(run, root):
    run("couple", "--artifact-root", root, "--use-case", "lint", "--tool", "ruff",
        "--couple", "pyproject.toml|config|edit", "--couple", "x.py|reference|entangled")
    text = _summary(root)
    assert "Tool Entanglement" in text
    assert "- ruff @ lint: 2 file(s), detachment: entangled" in text
