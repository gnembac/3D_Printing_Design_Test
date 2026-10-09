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


def test_min_feature_not_below_article_value() -> None:
    with pytest.raises(ValueError):
        replace(CardParams(), min_feature=0.4).validate()


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


def test_relief_and_recess_mesh_is_single_watertight_shell() -> None:
    for mod in ("shapely", "trimesh", "fontTools", "mapbox_earcut", "PIL"):
        pytest.importorskip(mod)
    from card_relief import build_front_relief
    from ncfai_card import build_mesh

    p = CardParams()
    rel = build_front_relief("Ada Lee", p.min_feature)
    assert rel.raised.area > 50 and rel.recess.area > 10
    geo = build_mesh(p, [], rel.raised, rel.recess).geometry()
    assert geo.is_watertight and len(geo.split()) == 1
    assert abs(geo.bounds[1][2] - p.total_thickness) < 1e-9
    # recessed letters remove material compared with the same card without recess
    no_recess = build_mesh(replace(p, recess_depth=0.0), [], rel.raised, rel.recess).geometry()
    assert geo.volume < no_recess.volume
    # flat control variant: plain 2.0 mm plate
    flat = build_mesh(replace(p, relief=0.0, recess_depth=0.0), [], None).geometry()
    assert flat.is_watertight and abs(flat.bounds[1][2] - 2.0) < 1e-9


def test_given_name_is_larger_than_family_name() -> None:
    pytest.importorskip("shapely")
    pytest.importorskip("fontTools")
    from card_relief import FAMILY_SIZE, GIVEN_SIZE, build_front_relief

    assert GIVEN_SIZE > FAMILY_SIZE
    rel = build_front_relief("Ada Lee", 0.5)
    x0, y0, x1, y1 = rel.name.bounds
    assert y1 - y0 > 0 and x0 >= 5.0 - 0.1


def test_overlong_list_line_is_rejected() -> None:
    pytest.importorskip("shapely")
    pytest.importorskip("fontTools")
    from card_relief import build_front_relief

    with pytest.raises(ValueError):
        build_front_relief("A B", 0.5, doemens="DOEMENS BIERSOMMELIER UND SENSORIK")


def test_recess_floor_not_below_general_mjf_wall() -> None:
    with pytest.raises(ValueError):
        replace(CardParams(), recess_depth=0.8).validate()  # floor 1.2 < 1.5


def test_icons_respect_min_feature() -> None:
    pytest.importorskip("shapely")
    from card_relief import chip_icon, enforce_min_feature, robot_head

    for g in (robot_head(0, 0), chip_icon(0, 0)):
        kept = enforce_min_feature(g, 0.8)
        assert kept.symmetric_difference(g).area / g.area < 0.08


def test_3mf_exports_are_single_watertight_shells(tmp_path: Path) -> None:
    for mod in ("shapely", "trimesh", "fontTools", "mapbox_earcut", "PIL", "triangle", "lxml"):
        pytest.importorskip(mod)
    import zipfile

    import trimesh
    from card_relief import build_front_relief
    from export_3mf import merge_mesh, write_texture_3mf, write_vcolor_3mf
    from ncfai_card import build_mesh
    from PIL import Image

    p = CardParams()
    rel = build_front_relief("Ada Lee", p.min_feature)
    img = Image.new("RGB", (340, 220), (200, 120, 40))
    coarse = build_mesh(p, [], rel.raised, rel.recess)
    mm = merge_mesh(coarse.verts, coarse.uv, coarse.groups)
    tex = tmp_path / "t.3mf"
    write_texture_3mf(tex, mm, img, img)
    xml = zipfile.ZipFile(tex).read("3D/3dmodel.model").decode()
    assert "texture2dgroup" in xml and xml.count("<triangle ") == len(mm.faces)
    assert trimesh.load(tex, force="mesh").is_watertight

    dense = build_mesh(p, [], rel.raised, rel.recess, max_area=0.5, segment=1.0)
    mmd = merge_mesh(dense.verts, dense.uv, dense.groups)
    vc = tmp_path / "v.3mf"
    write_vcolor_3mf(vc, mmd, img, img, p.width, p.height)
    xml = zipfile.ZipFile(vc).read("3D/3dmodel.model").decode()
    assert "colorgroup" in xml and xml.count("<triangle ") == len(mmd.faces)
    m = trimesh.load(vc, force="mesh")
    assert m.is_watertight and len(m.split()) == 1
