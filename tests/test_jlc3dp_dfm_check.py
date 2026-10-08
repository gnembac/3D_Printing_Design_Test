import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from jlc3dp_dfm_check import (  # noqa: E402
    RULES_CSV,
    PartFeatures,
    check_part,
    general_tolerance_mm,
    governing_min,
    load_rules,
    min_wall_mm,
)

DATA_DIR = RULES_CSV.parent
RULES = load_rules()


def test_rules_csv_loads_and_has_all_processes() -> None:
    assert {r.process for r in RULES} >= {"FDM", "SLA", "SLS", "MJF", "SLM"}


def test_conflicting_sources_resolve_to_conservative_value() -> None:
    assert governing_min(RULES, "FDM", "hole_dia_min") == 3.0
    assert governing_min(RULES, "FDM", "detail_min") == 1.0
    assert governing_min(RULES, "MJF", "detail_min") == 0.8


def test_min_wall_by_size_class() -> None:
    assert min_wall_mm(RULES, "SLA", 5) == 0.5
    assert min_wall_mm(RULES, "SLA", 60) == 1.5
    assert min_wall_mm(RULES, "FDM", 30) == 1.6
    assert min_wall_mm(RULES, "FDM", 400) == 2.5  # extrapolated from 200 mm class


def test_general_tolerance_switches_to_relative_above_limit() -> None:
    assert general_tolerance_mm(RULES, "FDM", 80) == 0.3
    assert general_tolerance_mm(RULES, "FDM", 200) == 0.8
    assert general_tolerance_mm(RULES, "SLA", 150) == 0.45
    assert general_tolerance_mm(RULES, "BJ", 80) == 1.04


def test_check_part_flags_violations() -> None:
    part = PartFeatures(
        process="FDM",
        max_dim_mm=80,
        wall_mm=1.6,
        hole_dia_mm=2.0,
        hole_depth_mm=8.0,
        vent_hole_dia_mm=2.6,
        vent_hole_count=1,
    )
    results = {f.rule_id: f.passed for f in check_part(part, RULES)}
    assert results["wall_min"] is False  # needs 2.0 mm at 80 mm part size
    assert results["hole_dia_min"] is False
    assert results["hole_depth_ratio_max"] is False  # 8 / 2 = 4 > 3
    assert results["vent_hole_count"] is False  # < 3.0 mm needs two holes


def test_check_part_passes_compliant_part() -> None:
    part = PartFeatures(
        process="SLS",
        max_dim_mm=40,
        wall_mm=1.5,
        hole_dia_mm=2.0,
        hole_depth_mm=6.0,
        clearance_moving_mm=0.6,
        vent_hole_dia_mm=3.5,
    )
    assert all(f.passed for f in check_part(part, RULES))


def test_mechanical_properties_reference_known_materials() -> None:
    overview = DATA_DIR / "jlc3dp_materials_overview_2026-10-08.csv"
    mechanical = DATA_DIR / "jlc3dp_mechanical_properties_2026-10-08.csv"
    with overview.open(newline="", encoding="utf-8") as handle:
        known = {row["material_id"] for row in csv.DictReader(handle)}
    with mechanical.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["material_id"] for row in rows} <= known
    for row in rows:
        assert row["unit"], row
        assert row["quality_flag"], row
