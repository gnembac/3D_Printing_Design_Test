import sys
from dataclasses import replace
from pathlib import Path

import pytest

CARD_DIR = (
    Path(__file__).resolve().parent.parent / "cad" / "functional-prototypes" / "ncfai-business-card"
)
sys.path.insert(0, str(CARD_DIR))

from card_params import CardParams, layout_bubbles, min_ligament, seed_tag  # noqa: E402


def test_defaults_valid() -> None:
    CardParams().validate()


def test_thickness_window_respects_wall_min_and_max() -> None:
    with pytest.raises(ValueError):
        replace(CardParams(), thickness=1.9).validate()
    with pytest.raises(ValueError):
        replace(CardParams(), thickness=2.3).validate()  # 2.3 + 0.3 tol > 2.5


def test_layout_is_reproducible_and_seed_dependent() -> None:
    p = CardParams()
    assert layout_bubbles(p) == layout_bubbles(p)
    assert layout_bubbles(p) != layout_bubbles(replace(p, seed="OTHER"))
    assert seed_tag("A") != seed_tag("B")


def test_layout_keeps_webs_and_edge_distance() -> None:
    p = CardParams()
    b = layout_bubbles(p)
    assert len(b) == p.n_bubbles
    assert min_ligament(p, b) >= p.edge_margin - p.bubble_d_max / 2 and min_ligament(p, b) >= 2.0


def test_flat_control_variant_has_no_holes() -> None:
    assert layout_bubbles(replace(CardParams(), n_bubbles=0)) == []


def test_overfull_zone_raises() -> None:
    with pytest.raises(ValueError):
        layout_bubbles(replace(CardParams(), n_bubbles=60))
