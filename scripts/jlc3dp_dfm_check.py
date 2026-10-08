"""Design-for-manufacturing pre-check against JLC3DP published design rules.

Rule source: data/material-datasheets/jlc3dp/jlc3dp_design_rules_<date>.csv
(manufacturer data, see docs/reference/jlc3dp/README.md).

Where the source contradicts itself (e.g. FDM minimum hole 1.5 mm vs 3.0 mm),
the conservative value governs. This is a screening aid for a supplier
package; it does not replace the supplier's own DFM feedback.

Usage:
    python scripts/jlc3dp_dfm_check.py FDM --max-dim 80 --wall 1.8 --hole-dia 3.2
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

RULES_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "material-datasheets"
    / "jlc3dp"
    / "jlc3dp_design_rules_2026-10-08.csv"
)


@dataclass(frozen=True)
class Rule:
    process: str
    rule_id: str
    applies_to_size_max_mm: float | None
    value_min: float | None
    value_max: float | None
    unit: str
    source: str
    quality_flag: str


@dataclass(frozen=True)
class PartFeatures:
    """Geometry features to check. None means 'not present / not checked'."""

    process: str
    max_dim_mm: float
    wall_mm: float | None = None
    feature_wall_mm: float | None = None
    detail_mm: float | None = None
    hole_dia_mm: float | None = None
    hole_depth_mm: float | None = None
    pin_dia_mm: float | None = None
    pin_height_mm: float | None = None
    clearance_assembly_mm: float | None = None
    clearance_moving_mm: float | None = None
    vent_hole_dia_mm: float | None = None
    vent_hole_count: int | None = None
    thread_pitch_mm: float | None = None


@dataclass(frozen=True)
class Finding:
    rule_id: str
    passed: bool
    message: str


def _to_float(text: str) -> float | None:
    text = text.strip()
    return float(text) if text else None


def load_rules(path: Path = RULES_CSV) -> list[Rule]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            Rule(
                process=row["process"],
                rule_id=row["rule_id"],
                applies_to_size_max_mm=_to_float(row["applies_to_size_max_mm"]),
                value_min=_to_float(row["value_min"]),
                value_max=_to_float(row["value_max"]),
                unit=row["unit"],
                source=row["source"],
                quality_flag=row["quality_flag"],
            )
            for row in csv.DictReader(handle)
        ]


def _select(rules: list[Rule], process: str, rule_id: str) -> list[Rule]:
    return [r for r in rules if r.process == process and r.rule_id == rule_id]


def governing_min(rules: list[Rule], process: str, rule_id: str) -> float | None:
    """Largest (most conservative) minimum value across all sources."""
    values = [r.value_min for r in _select(rules, process, rule_id) if r.value_min is not None]
    return max(values) if values else None


def governing_max(rules: list[Rule], process: str, rule_id: str) -> float | None:
    """Smallest (most conservative) maximum value across all sources."""
    values = [r.value_max for r in _select(rules, process, rule_id) if r.value_max is not None]
    return min(values) if values else None


def min_wall_mm(rules: list[Rule], process: str, max_dim_mm: float) -> float | None:
    """Minimum wall thickness for the part size class.

    Uses the first size class whose upper bound covers the part; parts larger
    than the largest class use the largest class value (extrapolation).
    """
    sized = sorted(
        (r for r in _select(rules, process, "wall_min") if r.applies_to_size_max_mm is not None),
        key=lambda r: r.applies_to_size_max_mm or 0.0,
    )
    if not sized:
        return None
    for rule in sized:
        if max_dim_mm <= (rule.applies_to_size_max_mm or 0.0):
            return rule.value_min
    return sized[-1].value_min


def general_tolerance_mm(rules: list[Rule], process: str, nominal_mm: float) -> float | None:
    """Symmetric general tolerance (+/- mm) for a nominal dimension."""
    abs_rules = _select(rules, process, "tol_general_abs")
    rel_value = governing_max(rules, process, "tol_general_rel")
    if not abs_rules or rel_value is None:
        return None
    limit = abs_rules[0].applies_to_size_max_mm or 0.0
    if nominal_mm <= limit:
        return abs_rules[0].value_max
    return round(nominal_mm * rel_value / 100.0, 4)


def _check_min(
    rules: list[Rule], process: str, rule_id: str, actual: float | None
) -> Finding | None:
    if actual is None:
        return None
    limit = governing_min(rules, process, rule_id)
    if limit is None:
        return Finding(rule_id, True, f"no {process} rule published (k.A.)")
    passed = actual >= limit
    return Finding(rule_id, passed, f"{actual} mm vs min {limit} mm")


def check_part(part: PartFeatures, rules: list[Rule] | None = None) -> list[Finding]:
    rules = load_rules() if rules is None else rules
    p = part.process
    findings: list[Finding] = []

    if part.wall_mm is not None:
        limit = min_wall_mm(rules, p, part.max_dim_mm)
        if limit is None:
            findings.append(Finding("wall_min", True, f"no {p} rule published (k.A.)"))
        else:
            findings.append(
                Finding(
                    "wall_min",
                    part.wall_mm >= limit,
                    f"{part.wall_mm} mm vs min {limit} mm for part size {part.max_dim_mm} mm",
                )
            )

    for rule_id, actual in (
        ("wall_min_feature", part.feature_wall_mm),
        ("detail_min", part.detail_mm),
        ("hole_dia_min", part.hole_dia_mm),
        ("pin_dia_min", part.pin_dia_mm),
        ("clearance_assembly_min", part.clearance_assembly_mm),
        ("clearance_moving_min", part.clearance_moving_mm),
        ("vent_hole_min", part.vent_hole_dia_mm),
        ("thread_pitch_min", part.thread_pitch_mm),
    ):
        finding = _check_min(rules, p, rule_id, actual)
        if finding is not None:
            findings.append(finding)

    for rule_id, num, den in (
        ("hole_depth_ratio_max", part.hole_depth_mm, part.hole_dia_mm),
        ("pin_height_ratio_max", part.pin_height_mm, part.pin_dia_mm),
    ):
        if num is None or not den:
            continue
        limit = governing_max(rules, p, rule_id)
        ratio = num / den
        if limit is not None:
            findings.append(
                Finding(rule_id, ratio <= limit, f"ratio {ratio:.2f} vs max {limit:.2f}")
            )

    if part.vent_hole_dia_mm is not None and part.vent_hole_dia_mm < 3.0:
        count = part.vent_hole_count or 1
        findings.append(
            Finding(
                "vent_hole_count",
                count >= 2,
                f"{count} vent hole(s) of {part.vent_hole_dia_mm} mm; >= 2 required below 3.0 mm",
            )
        )

    return findings


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("process", choices=["FDM", "SLA", "SLS", "MJF", "SLM"])
    parser.add_argument("--max-dim", type=float, required=True, help="largest part dimension, mm")
    for name in (
        "wall",
        "feature-wall",
        "detail",
        "hole-dia",
        "hole-depth",
        "pin-dia",
        "pin-height",
        "clearance-assembly",
        "clearance-moving",
        "vent-hole-dia",
        "thread-pitch",
    ):
        parser.add_argument(f"--{name}", type=float)
    parser.add_argument("--vent-hole-count", type=int)
    args = parser.parse_args()

    part = PartFeatures(
        process=args.process,
        max_dim_mm=args.max_dim,
        wall_mm=args.wall,
        feature_wall_mm=args.feature_wall,
        detail_mm=args.detail,
        hole_dia_mm=args.hole_dia,
        hole_depth_mm=args.hole_depth,
        pin_dia_mm=args.pin_dia,
        pin_height_mm=args.pin_height,
        clearance_assembly_mm=args.clearance_assembly,
        clearance_moving_mm=args.clearance_moving,
        vent_hole_dia_mm=args.vent_hole_dia,
        vent_hole_count=args.vent_hole_count,
        thread_pitch_mm=args.thread_pitch,
    )
    rules = load_rules()
    findings = check_part(part, rules)
    tol = general_tolerance_mm(rules, part.process, part.max_dim_mm)
    print(f"General tolerance at {part.max_dim_mm} mm: +/-{tol} mm (manufacturer data)")
    for f in findings:
        print(f"[{'PASS' if f.passed else 'FAIL'}] {f.rule_id}: {f.message}")
    return 0 if all(f.passed for f in findings) else 1


if __name__ == "__main__":
    raise SystemExit(_main())
