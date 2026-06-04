#!/usr/bin/env python3
"""Small shared runtime helpers for ADOP CLI."""

from __future__ import annotations

import io
import sys


def fix_stdout_encoding() -> None:
    """Prefer UTF-8 stdout so JSON output stays readable on Windows shells."""
    stream = sys.stdout
    if not hasattr(stream, "buffer"):
        return
    encoding = getattr(stream, "encoding", None)
    if encoding and encoding.lower() == "utf-8":
        return
    try:
        sys.stdout = io.TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        return
