#!/usr/bin/env python3
"""ADOP artifact id helpers."""

from __future__ import annotations

import re
from pathlib import Path

# Accept 3-or-more digits: format_id zero-pads to 3 but ids >= 1000 widen to 4+.
# Keeping a fixed \d{3} here would make parse_numeric_id reject pm-1000 and break
# next_sequential_id / latest ordering past 999 (residual B12).
ID_PATTERN = re.compile(r"^(?P<prefix>[a-z]+)-(?P<number>\d{3,})$")


def format_id(prefix: str, number: int) -> str:
    return f"{prefix}-{number:03d}"


def parse_numeric_id(value: str, prefix: str) -> int | None:
    match = ID_PATTERN.match(value)
    if not match or match.group("prefix") != prefix:
        return None
    return int(match.group("number"))


def next_sequential_id(root: Path, prefix: str) -> str:
    root = root.resolve()
    max_number = 0
    for path in root.glob("adop_*_*.json"):
        artifact_id = path.stem.rsplit("_", 1)[-1]
        number = parse_numeric_id(artifact_id, prefix)
        if number is not None:
            max_number = max(max_number, number)
    return format_id(prefix, max_number + 1)
