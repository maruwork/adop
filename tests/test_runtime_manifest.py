"""Phase 1 (C1): the manifest + sync must carry the renderer and its template."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((REPO / "adop.json").read_text(encoding="utf-8"))


def test_renderer_is_in_runtime_files():
    assert "shared/python/adop_html.py" in MANIFEST["runtime_files"]


def test_template_is_declared():
    assert "shared/templates/adop-governance-dashboard-template.html" in MANIFEST.get("template_files", [])


def test_manifest_synced_runtime_starts_and_renders(tmp_path: Path):
    target = tmp_path / "proj"
    for rel in MANIFEST["runtime_files"] + MANIFEST.get("template_files", []):
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dst)
    cli = target / "shared/python/adop_cli.py"
    version = subprocess.run([sys.executable, str(cli), "--version"], capture_output=True, text=True)
    assert version.returncode == 0, version.stderr
    out = target / "out.html"
    rendered = subprocess.run(
        [sys.executable, str(cli), "render-html", "--artifact-root", str(target / ".adop"), "--output", str(out)],
        capture_output=True, text=True,
    )
    # render-html tolerates an empty/absent root by creating an empty board.
    assert rendered.returncode == 0, rendered.stderr
    assert out.exists()
