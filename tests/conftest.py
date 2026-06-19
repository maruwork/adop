"""Shared test fixtures and import-path setup for the ADOP test suite.

The runtime modules live under shared/python/ and use a try/except import
pattern (package vs. script). Tests import them as top-level modules, so we
prepend shared/python/ to sys.path here.
"""

from __future__ import annotations

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent.parent / "shared" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import adop_artifacts as artifacts  # noqa: E402
import pytest  # noqa: E402
from adop_cli import main  # noqa: E402


@pytest.fixture
def root(tmp_path: Path) -> str:
    """A bounded artifact root outside any target project."""
    return str(tmp_path)


@pytest.fixture
def run():
    """Run the CLI by argv list, returning the process-style exit code."""

    def _run(*argv: str) -> int:
        return main(list(argv))

    return _run


@pytest.fixture
def latest():
    """Read the latest artifact of a type for a scene from an artifact root."""

    def _latest(root: str, artifact_type: str, *, scene: str | None = None):
        return artifacts.latest_by_type(Path(root), artifact_type, scene=scene)

    return _latest


def promote_scene(run, root: str, *, scene: str = "lint", tool: str = "pylint") -> None:
    """Drive a scene through intake -> compare -> trial -> promote.

    Leaves the scene in the `promote` state so retirement transitions can run.
    """
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", tool, "--source", "doc",
        "--use-case", scene, "--why-now", "need bounded trial",
        "--platform", "any",
        "--license", "MIT",
        "--cost", "free",
        "--version", "1.0.0",
        "--category", "cli",
        "--ai-compatibility", "any",
        "--data-flow-json", '{"destination":"local","data_types":["code"],"opt_in":true}',
    ) == 0
    assert run(
        "quick-compare", "--artifact-root", root, "--use-case", scene,
        "--candidate", tool, "--candidate", "other-tool", "--selected", tool,
    ) == 0
    assert run(
        "quick-trial", "--artifact-root", root, "--use-case", scene,
        "--mode", "read-only-comparison", "--executor", "ci",
        "--decision-owner", "lead", "--landing-target", "ci/lint",
    ) == 0
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", "tr-001", "--verdict", "promote",
        "--observed-effect", "works",
        "--judgment-reason", "trial produced reusable value",
        "--next-action", "promote into the lint workflow",
        "--recurring-control-decision", "yes",
        "--root-cause-hypothesis", "lint evaluation needed a stable reusable helper",
        "--preventive-action", "document the approved lint usage scene",
        "--why-this-problem-recurred", "the team had no explicit adoption record before the trial",
    ) == 0
