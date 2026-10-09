import sys
from dataclasses import replace
from pathlib import Path

import pytest

COUPON_DIR = (
    Path(__file__).resolve().parent.parent
    / "cad"
    / "test-specimens"
    / "ex002-hinge-clearance-coupon"
)
sys.path.insert(0, str(COUPON_DIR))

from hinge_params import DEFAULT_CLEARANCES, HingeParams, series  # noqa: E402


def test_defaults_valid() -> None:
    HingeParams().validate()


def test_series_covers_mjf_rule_boundary() -> None:
    assert min(DEFAULT_CLEARANCES) < 0.6 <= max(DEFAULT_CLEARANCES)
    assert len(series()) == len(DEFAULT_CLEARANCES)


def test_axial_layout_adds_up() -> None:
    p = HingeParams(clearance=0.8)
    assert 3 * p.knuckle_len + 2 * p.clearance == pytest.approx(p.axis_len)


def test_bore_and_knuckle_diameter() -> None:
    p = HingeParams(clearance=0.6, pin_d=2.5, knuckle_wall=2.5)
    assert p.bore_d == pytest.approx(3.7)
    assert p.knuckle_d == pytest.approx(8.7)


def test_mjf_findings_flag_small_clearance_only() -> None:
    assert HingeParams(clearance=0.4).mjf_findings() != []
    assert HingeParams(clearance=0.6).mjf_findings() == []


@pytest.mark.parametrize(
    "bad",
    [
        {"clearance": 0.0},
        {"pin_d": -1.0},
        {"axis_len": 10.0},
        {"leaf_w": 3.0},
    ],
)
def test_invalid_parameters_rejected(bad: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        replace(HingeParams(), **bad).validate()
