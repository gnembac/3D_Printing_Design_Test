import sys
from dataclasses import replace
from pathlib import Path

import pytest

BADGE_DIR = (
    Path(__file__).resolve().parent.parent / "cad" / "functional-prototypes" / "bjcp-judge-badge"
)
sys.path.insert(0, str(BADGE_DIR))

from badge_params import BadgeParams  # noqa: E402


def test_defaults_valid() -> None:
    BadgeParams().validate()


def test_z_levels_are_layer_multiples() -> None:
    p = BadgeParams()
    for z in (p.z_field, p.z_relief, p.z_top, p.pocket_depth):
        assert abs(z / p.layer_height - round(z / p.layer_height)) < 1e-9


@pytest.mark.parametrize("bad", ["5689", "E568", "e5689", "EE5689", ""])
def test_rejects_bad_bjcp_id(bad: str) -> None:
    with pytest.raises(ValueError):
        replace(BadgeParams(), bjcp_id=bad).validate()


def test_rejects_off_grid_thickness() -> None:
    with pytest.raises(ValueError):
        replace(BadgeParams(), relief=0.75).validate()


def test_rejects_thin_floor_above_magnet_pocket() -> None:
    with pytest.raises(ValueError):
        replace(BadgeParams(), base_thickness=2.8).validate()


def test_rejects_magnets_too_close_to_rim() -> None:
    with pytest.raises(ValueError):
        replace(BadgeParams(), magnet_spacing=96.0).validate()


def test_rejects_thin_counter_plate_wall() -> None:
    with pytest.raises(ValueError):
        replace(BadgeParams(), plate_w=41.0).validate()


def test_geometry_build_if_cadquery_available() -> None:
    pytest.importorskip("cadquery")
    import bjcp_badge

    solids = bjcp_badge.build(BadgeParams())
    assert set(solids) == {"black", "orange", "blue", "white", "amber", "counterplate"}
    assert bjcp_badge.check_fit(BadgeParams(), solids) == []
