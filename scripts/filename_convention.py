"""Parse and validate the project filename convention.

Convention (see .claude/CLAUDE.md "Source of truth and revisions"):
[project]_[part-number]_[revision]_[process]_[material]_[YYYY-MM-DD].[extension]

Example: DOE003_warping-coupon_R02_FDM_ASA_2026-10-04.step
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_PATTERN = re.compile(
    r"^(?P<project>[^_]+)_(?P<part_number>[^_]+)_(?P<revision>R\d{2}|EXP|REL)_"
    r"(?P<process>[^_]+)_(?P<material>[^_]+)_"
    r"(?P<date>\d{4}-\d{2}-\d{2})\.(?P<extension>[A-Za-z0-9]+)$"
)


@dataclass(frozen=True)
class ParsedFilename:
    project: str
    part_number: str
    revision: str
    process: str
    material: str
    date: str
    extension: str


def parse_filename(filename: str) -> ParsedFilename | None:
    """Parse a filename against the project convention.

    Returns None if the filename does not match the convention.
    """
    match = _PATTERN.match(filename)
    if match is None:
        return None
    return ParsedFilename(**match.groupdict())


def is_valid_filename(filename: str) -> bool:
    return parse_filename(filename) is not None
