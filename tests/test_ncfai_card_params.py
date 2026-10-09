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


def test_envelope_respects_wall_min_and_max() -> None:
    assert CardParams().total_thickness == 2.5
    with pytest.raises(ValueError):
        replace(CardParams(), base_thickness=1.9).validate()
    with pytest.raises(ValueError):
        replace(CardParams(), relief=0.8).validate()  # 2.0 + 0.8 > 2.5
    with pytest.raises(ValueError):
        replace(CardParams(), relief=0.3).validate()  # below minimum relief depth
    replace(CardParams(), relief=0.0).validate()  # flat control variant


def test_min_feature_not_below_supplier_value() -> None:
    with pytest.raises(ValueError):
        replace(CardParams(), min_feature=0.5).validate()


def test_layout_is_reproducible_and_seed_dependent() -> None:
    p = replace(CardParams(), n_bubbles=7)
    assert layout_bubbles(p) == layout_bubbles(p)
    assert layout_bubbles(p) != layout_bubbles(replace(p, seed="OTHER"))
    assert seed_tag("A") != seed_tag("B")


def test_layout_keeps_webs_and_edge_distance() -> None:
    p = replace(CardParams(), n_bubbles=7)
    b = layout_bubbles(p)
    assert len(b) == p.n_bubbles
    assert min_ligament(p, b) >= p.edge_margin - p.bubble_d_max / 2 and min_ligament(p, b) >= 2.0


def test_flat_control_variant_has_no_holes() -> None:
    assert layout_bubbles(CardParams()) == []


def test_overfull_zone_raises() -> None:
    with pytest.raises(ValueError):
        layout_bubbles(replace(CardParams(), n_bubbles=60))


def test_qr_layout_geometry() -> None:
    pytest.importorskip("segno")
    from card_qr import QUIET_MODULES, make_layout

    q = make_layout("https://example.com/", right=78.0, top=7.0, ppmm=40.0)
    assert q.n in (25, 29, 33)  # version 2-4 at ECC Q
    assert abs(q.module_mm * 40 - round(q.module_mm * 40)) < 1e-9  # integer pixels per module
    assert q.module_mm >= 1.0
    assert abs(q.x + q.size - 78.0) < 1e-9
    x0, _, x1, _ = q.keep_out
    assert abs((q.x - x0) - QUIET_MODULES * q.module_mm) < 1e-9 and x1 > q.x + q.size


def test_relief_mesh_is_single_watertight_shell_with_engraved_badge() -> None:
    for mod in ("shapely", "trimesh", "fontTools", "mapbox_earcut", "PIL"):
        pytest.importorskip(mod)
    from card_relief import build_front_relief, parts
    from ncfai_card import build_mesh

    p = CardParams()
    rel = build_front_relief("Ada Lee", ("EXAMPLE", "WORD"), 7, p.min_feature)
    assert rel.raised.area > 100 and len(rel.cone.tiles) > 8
    geo = build_mesh(p, [], rel.raised).geometry()
    assert geo.is_watertight and len(geo.split()) == 1
    assert abs(geo.bounds[1][2] - p.total_thickness) < 1e-9
    # engraved letters leave holes in the raised badge polygons
    assert any(len(q.interiors) > 0 for q in parts(rel.badges))
    # flat control variant: plain 2.0 mm plate
    flat = build_mesh(replace(p, relief=0.0), [], None).geometry()
    assert flat.is_watertight and abs(flat.bounds[1][2] - 2.0) < 1e-9


def test_relief_is_seed_dependent() -> None:
    pytest.importorskip("shapely")
    pytest.importorskip("fontTools")
    from card_relief import build_front_relief

    a = build_front_relief("A B", ("X",), 1, 0.8).cone.tiles
    b = build_front_relief("A B", ("X",), 2, 0.8).cone.tiles
    assert [t.wkt for t, _ in a] != [t.wkt for t, _ in b]
