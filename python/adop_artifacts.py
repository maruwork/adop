#!/usr/bin/env python3
"""ADOP JSON artifact IO."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from typing import Callable

try:
    from .adop_ids import next_sequential_id, parse_numeric_id
    from .adop_types import JUDGMENT_REPORT, SCHEMA_VERSION, TRIAL_PACKET
except ImportError:  # pragma: no cover - script import path
    from adop_ids import next_sequential_id, parse_numeric_id
    from adop_types import JUDGMENT_REPORT, SCHEMA_VERSION, TRIAL_PACKET


class AdopArtifactError(ValueError):
    """Artifact IO or schema error."""


def _validate_root_boundary(
    resolved: Path,
    *,
    target_project_root: Path | None,
    allow_project_impact: bool,
) -> None:
    """Reject an artifact root that overlaps the target project (both directions).

    Resolving with strict=False follows symlinks where possible so a symlinked
    artifact root cannot smuggle writes back into the project (residual B38).
    """
    if target_project_root is None or allow_project_impact:
        return
    project_root = target_project_root.resolve()
    if resolved == project_root:
        raise AdopArtifactError(
            "artifact-root must be outside target-project-root when project impact is not allowed"
        )
    # Bidirectional containment: artifact-root inside project, OR project inside artifact-root.
    if resolved.is_relative_to(project_root) or project_root.is_relative_to(resolved):
        raise AdopArtifactError(
            "artifact-root must be outside target-project-root when project impact is not allowed"
        )


def resolve_artifact_root(
    root: Path,
    *,
    target_project_root: Path | None = None,
    allow_project_impact: bool = False,
) -> Path:
    """Resolve and boundary-check an artifact root WITHOUT creating it.

    Read paths (load/find/latest/summary) use this so a mistyped root is not
    silently materialised as an empty tree (residual B39).
    """
    resolved = root.resolve()
    _validate_root_boundary(
        resolved,
        target_project_root=target_project_root,
        allow_project_impact=allow_project_impact,
    )
    return resolved


def ensure_artifact_root(
    root: Path,
    *,
    target_project_root: Path | None = None,
    allow_project_impact: bool = False,
) -> Path:
    """Resolve, boundary-check, AND create the artifact root (write paths)."""
    resolved = resolve_artifact_root(
        root,
        target_project_root=target_project_root,
        allow_project_impact=allow_project_impact,
    )
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def artifact_filename(artifact_type: str, artifact_id: str) -> str:
    return f"adop_{artifact_type}_{artifact_id}.json"


def artifact_path(root: Path, artifact_type: str, artifact_id: str) -> Path:
    return ensure_artifact_root(root) / artifact_filename(artifact_type, artifact_id)


def write_artifact(root: Path, artifact_type: str, artifact_id: str, payload: dict[str, Any]) -> Path:
    path = artifact_path(root, artifact_type, artifact_id)
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    lock_path = path.with_name(f".{path.name}.lock")
    # Atomic write: a crash mid-write must not leave a truncated JSON file that
    # would later poison load_all_artifacts (residual B36). Write to a temp file
    # in the same directory, fsync, then os.replace (atomic on the same volume).
    tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise AdopArtifactError(f"artifact write already in progress: {path.name}") from exc
    try:
        os.close(fd)
        if path.exists():
            raise AdopArtifactError(f"artifact already exists: {path.name}")
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
        if lock_path.exists():
            lock_path.unlink()
    return path


def write_artifact_group(
    root: Path,
    specs: list[tuple[str, str, dict[str, Any]]],
) -> list[Path]:
    """Write a set of artifacts as a bounded grouped commit (residual B14).

    `specs` is a list of (artifact_type, artifact_id, payload). The whole group
    is staged to temp files first; only after EVERY stage succeeds are the temps
    promoted with os.replace. If any stage or commit fails, files already
    committed in this call are removed (best-effort rollback) so callers like
    close-trial never leave a half-written multi-artifact set. This is not a true
    database transaction (a crash between two os.replace calls can still leave a
    partial set), but it removes the validate/serialize failure window that
    previously wrote some artifacts before erroring on a later one.
    """
    resolved = ensure_artifact_root(root)
    staged: list[tuple[Path, Path]] = []  # (final_path, tmp_path) ready to commit
    locks: list[Path] = []  # every lock acquired, registered for cleanup before any raise
    tmps: list[Path] = []  # every temp created, registered for cleanup before any raise
    committed: list[Path] = []
    try:
        # Phase 1: lock + stage every artifact to a temp file (no final paths yet).
        for artifact_type, artifact_id, payload in specs:
            path = resolved / artifact_filename(artifact_type, artifact_id)
            lock_path = path.with_name(f".{path.name}.lock")
            tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError as exc:
                raise AdopArtifactError(f"artifact write already in progress: {path.name}") from exc
            # Register the lock for cleanup immediately — before any raise below —
            # so a collision cannot leak a stale .lock file.
            locks.append(lock_path)
            os.close(fd)
            if path.exists():
                raise AdopArtifactError(f"artifact already exists: {path.name}")
            tmps.append(tmp_path)
            body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            with open(tmp_path, "w", encoding="utf-8") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((path, tmp_path))
        # Phase 2: commit every staged temp.
        for path, tmp_path in staged:
            os.replace(tmp_path, path)
            committed.append(path)
    except BaseException:
        # Best-effort rollback of anything already committed in THIS group.
        for path in committed:
            try:
                path.unlink()
            except OSError:
                pass
        raise
    finally:
        for tmp_path in tmps:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
        for lock_path in locks:
            if lock_path.exists():
                try:
                    lock_path.unlink()
                except OSError:
                    pass
    return committed


def write_next_sequential_artifact(
    root: Path,
    artifact_type: str,
    prefix: str,
    payload_factory: Callable[[str], dict[str, Any]],
    *,
    max_attempts: int = 64,
) -> tuple[str, Path]:
    """Mint the next sequential id and write it under exclusive lock (residual B13).

    `next_sequential_id` (scan-max+1) followed by a later write is not atomic, so
    two concurrent writers can mint the same id and one would hard-fail. Here we
    retry: mint -> build payload via payload_factory(id) -> attempt the exclusive
    atomic write; if that id was just taken by another writer ("already exists" /
    "already in progress"), advance to the next id and retry, bounded by
    max_attempts. Returns the (artifact_id, path) actually written.
    """
    resolved = ensure_artifact_root(root)
    last_error: AdopArtifactError | None = None
    for _ in range(max_attempts):
        artifact_id = next_sequential_id(resolved, prefix)
        payload = payload_factory(artifact_id)
        try:
            path = write_artifact(resolved, artifact_type, artifact_id, payload)
        except AdopArtifactError as exc:
            last_error = exc
            continue
        return artifact_id, path
    raise AdopArtifactError(
        f"could not reserve a free {artifact_type} id after {max_attempts} attempts"
        + (f": {last_error}" if last_error else "")
    )


def read_artifact(path: Path) -> dict[str, Any]:
    # utf-8-sig tolerates a BOM that other tools may prepend (residual B40).
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise AdopArtifactError(f"artifact must be JSON object: {path}")
    return payload


def _filename_type(path: Path) -> str | None:
    """Extract the artifact_type segment from adop_<type>_<id>.json, if shaped so."""
    stem = path.stem
    if not stem.startswith("adop_"):
        return None
    middle = stem[len("adop_"):]
    if "_" not in middle:
        return None
    return middle.rsplit("_", 1)[0]


def load_all_artifacts(root: Path) -> list[dict[str, Any]]:
    """Load every adop artifact under root.

    One malformed/unreadable file is skipped with a warning instead of aborting
    the whole load (residual B32); a filename/body artifact_type mismatch is
    also warned (residual B33). The returned dicts keep their original keys plus
    the reserved `_path`/`_adop_path` metadata keys.
    """
    resolved = resolve_artifact_root(root)
    if not resolved.exists():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(resolved.glob("adop_*_*.json")):
        try:
            payload = read_artifact(path)
        except (AdopArtifactError, json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            print(f"[adop] skipping unreadable artifact {path}: {exc}", file=sys.stderr)
            continue
        body_type = payload.get("artifact_type")
        name_type = _filename_type(path)
        if body_type is None:
            print(f"[adop] artifact missing artifact_type, classified by filename: {path}", file=sys.stderr)
        elif name_type is not None and body_type != name_type:
            print(
                f"[adop] artifact_type mismatch (filename={name_type}, body={body_type}): {path}",
                file=sys.stderr,
            )
        # Keep the historical `_path` key for backward compatibility, plus a
        # namespaced alias that is unlikely to collide with real artifact data.
        path_str = str(path)
        payload["_path"] = path_str
        payload["_adop_path"] = path_str
        items.append(payload)
    return items


def find_by_type(root: Path, artifact_type: str) -> list[dict[str, Any]]:
    return [item for item in load_all_artifacts(root) if item.get("artifact_type") == artifact_type]


def _id_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    """Numeric-aware sort key for artifact ids (residual B30/B31).

    String sort breaks once an id widens past 3 digits (`tr-1000` < `tr-999`).
    Sort by parsed number when possible; ids that do not parse sort last with a
    stable string tie-break so `latest` never silently returns an older record.
    """
    raw = str(item.get("artifact_id", ""))
    prefix = raw.split("-", 1)[0] if "-" in raw else ""
    number = parse_numeric_id(raw, prefix) if prefix else None
    if number is None:
        return (1, 0, raw)
    return (0, number, raw)


def latest_by_type(root: Path, artifact_type: str, *, scene: str | None = None) -> dict[str, Any] | None:
    items = find_by_type(root, artifact_type)
    if scene is not None:
        items = [item for item in items if item.get("related_scene") == scene]
    if not items:
        return None
    items.sort(key=_id_sort_key)
    return items[-1]


def _find_unique_by_id(root: Path, artifact_type: str, artifact_id: str) -> dict[str, Any] | None:
    if not artifact_id:
        return None
    matches = [item for item in find_by_type(root, artifact_type) if item.get("artifact_id") == artifact_id]
    if len(matches) > 1:
        raise AdopArtifactError(f"multiple {artifact_type} artifacts share id {artifact_id}")
    return matches[0] if matches else None


def find_trial_packet(root: Path, trial_id: str) -> dict[str, Any] | None:
    return _find_unique_by_id(root, TRIAL_PACKET, trial_id)


def find_judgment_report(root: Path, trial_id: str) -> dict[str, Any] | None:
    return _find_unique_by_id(root, JUDGMENT_REPORT, trial_id)


def json_response(command: str, status: str, artifact_refs: list[str], errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "status": status,
        "artifact_refs": artifact_refs,
        "errors": errors,
    }
