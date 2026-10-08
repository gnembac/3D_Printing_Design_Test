"""Parametric generator for a personal BJCP judge badge (multi-colour FDM, 0.2 mm nozzle).

Stack (z, mm; multiples of the 0.1 mm layer height):
    0.0 - 3.0   black back plate (rear magnet pockets, opt. lanyard tab)
    3.0 - 4.6   black rim ring
    3.0 - 3.8   orange fields (upper/lower) and blue name band
                (engraved drop-shadow grooves cut down to the black plate)
    3.8 - 5.0   raised white name (GUNTER large / NEMBACH small), 1.2 mm
    3.8 - 4.6   raised black text, amber hop + barley (black outline), 0.8 mm

A separate counter plate (worn inside the shirt) carries the mating magnets.

Usage (CadQuery required, see README.md):
    python bjcp_badge.py --out <dir> [--first-name Gunter --last-name Nembach ...]
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import sys
import zipfile
from dataclasses import replace
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from badge_params import BadgeParams  # noqa: E402

Solids = dict[str, cq.Workplane]


def _slab(shape2d: cq.Workplane, z0: float, h: float) -> cq.Workplane:
    return shape2d.extrude(h).translate((0, 0, z0))


def _ellipse(a: float, b: float, z0: float, h: float) -> cq.Workplane:
    return _slab(cq.Workplane("XY").ellipse(a, b), z0, h)


def _circle(cx: float, cy: float, r: float, z0: float, h: float) -> cq.Workplane:
    return _slab(cq.Workplane("XY").center(cx, cy).circle(r), z0, h)


def _rrect(w: float, h: float, r: float, cx: float, cy: float, z0: float, d: float) -> cq.Workplane:
    wp = cq.Workplane("XY").center(cx, cy).rect(w, h).extrude(d)
    return wp.edges("|Z").fillet(min(r, w / 2 - 0.01, h / 2 - 0.01)).translate((0, 0, z0))


def _poly(pts: list[tuple[float, float]], z0: float, h: float) -> cq.Workplane:
    return _slab(cq.Workplane("XY").polyline(pts).close(), z0, h)


def _rot(wp: cq.Workplane, cx: float, cy: float, deg: float) -> cq.Workplane:
    return wp.rotate((cx, cy, 0), (cx, cy, 1), deg)


def _text(
    p: BadgeParams, txt: str, size: float, cx: float, cy: float, z0: float, h: float
) -> cq.Workplane:
    """Text solid, bbox-centred on (cx, cy) (OCCT valign metrics are unreliable)."""
    t = cq.Workplane("XY").text(
        txt, size, h, combine=False, fontPath=p.font_path, halign="center", valign="center"
    )
    bb = t.val().BoundingBox()
    return t.translate((cx - (bb.xmin + bb.xmax) / 2, cy - (bb.ymin + bb.ymax) / 2, z0))


def _outline(sil: cq.Workplane, width: float, h: float) -> cq.Workplane:
    """Ring of `width` around `sil` by dilation (union of 16 shifted copies), minus `sil`.

    offset2D proved unreliable on thin features (barley awns); dilation is robust.
    """
    grown = sil
    for k in range(16):
        ang = 2 * math.pi * k / 16
        grown = grown.union(sil.translate((width * math.cos(ang), width * math.sin(ang), 0)))
    return grown.cut(sil)


def _hop(cx: float, cy: float, s: float, z0: float, h: float) -> tuple[cq.Workplane, cq.Workplane]:
    """Hop cone hanging from a stem. Returns (silhouette, engraved scale arcs)."""
    r = 1.9 * s
    rows = [
        (1.7, [0.0]),
        (3.9, [-1.3, 1.3]),
        (6.1, [-2.6, 0.0, 2.6]),
        (8.3, [-2.6, 0.0, 2.6]),
        (10.5, [-1.3, 1.3]),
    ]
    sil: cq.Workplane | None = None
    arcs: cq.Workplane | None = None
    lower_half = cq.Workplane("XY").box(40, 40, h + 2, centered=(True, False, False))
    for dy, xs in rows:
        for dx in xs:
            x, y = cx + dx * s, cy + dy * s
            c = _circle(x, y, r, z0, h)
            sil = c if sil is None else sil.union(c)
            ring = _circle(x, y, r - 0.1, z0 + h / 2, h).cut(
                _circle(x, y, r - 0.6 * s - 0.1, z0 + h / 2 - 1, h + 2)
            )
            half = lower_half.translate((x, y - 40, z0 - 1))
            arc = ring.intersect(half)
            arcs = arc if arcs is None else arcs.union(arc)
    assert sil is not None and arcs is not None
    stem = _rrect(0.9 * s, 3.2 * s, 0.3, cx, cy + 12.0 * s, z0, h)
    lx, ly = cx + 2.4 * s, cy + 13.0 * s
    leaf = _rot(
        _slab(cq.Workplane("XY").center(lx, ly).ellipse(2.3 * s, 1.0 * s), z0, h), lx, ly, 25
    )
    return sil.union(stem).union(leaf), arcs.intersect(sil)


def _barley(
    cx: float, cy: float, s: float, z0: float, h: float
) -> tuple[cq.Workplane, cq.Workplane]:
    """Barley ear. Returns (grains + stem [amber], short awns [black])."""
    ear = _rrect(0.9 * s, 12.0 * s, 0.3, cx, cy + 6.0 * s, z0, h)
    awns: cq.Workplane | None = None
    for i in range(4):
        y = cy + (3.4 + 2.5 * i) * s
        for sign in (-1, 1):
            gx = cx + sign * 1.1 * s
            g = _slab(cq.Workplane("XY").center(gx, y).ellipse(0.95 * s, 1.9 * s), z0, h)
            ear = ear.union(_rot(g, gx, y, -sign * 25))
    tip = _slab(cq.Workplane("XY").center(cx, cy + 13.4 * s).ellipse(0.95 * s, 1.9 * s), z0, h)
    ear = ear.union(tip)
    for i in range(4):
        y = cy + (3.4 + 2.5 * i) * s
        for sign in (-1, 1):
            gx = cx + sign * 1.1 * s
            x0, y0 = gx + sign * 0.5 * s, y + 1.6 * s
            x1, y1 = x0 + sign * 1.0 * s, y0 + 2.6 * s
            awn = _poly(
                [(x0, y0), (x0 + sign * 0.55, y0 + 0.1), (x1 + sign * 0.55, y1), (x1, y1)], z0, h
            )
            awns = awn if awns is None else awns.union(awn)
    assert awns is not None
    for dx in (-0.25 * s, 0.25 * s):
        awns = awns.union(
            _poly(
                [
                    (cx + dx - 0.25, cy + 14.8 * s),
                    (cx + dx + 0.25, cy + 14.8 * s),
                    (cx + dx * 3 + 0.25, cy + 16.0 * s),
                    (cx + dx * 3 - 0.25, cy + 17.2 * s),
                ],
                z0,
                h,
            )
        )
    return ear, awns.cut(ear)


def build(p: BadgeParams) -> Solids:
    """Return colour-name -> solid(s). Raises ValueError on invalid parameters."""
    p.validate()
    a, b, ia, ib = p.half_width, p.half_height, p.inner_a, p.inner_b
    zf, zr, zt = p.z_field, p.z_relief, p.z_top
    h, hn = p.relief, p.relief_name

    # --- black: plate + (opt. tab) + rim ring, rear magnet pockets --------------------
    plate = _ellipse(a, b, 0, zf)
    if p.lanyard_tab:
        tab_cy = b + p.tab_height / 2 - 2.0
        plate = plate.union(_rrect(p.tab_width, p.tab_height, 3.0, 0, tab_cy, 0, zf))
        slot = _rrect(p.slot_width, p.slot_height, p.slot_height / 2 - 0.01, 0, tab_cy, -1, zf + 2)
        plate = plate.cut(slot)
    for sx in (-1, 1):
        pocket = _circle(sx * p.magnet_spacing / 2, 0, p.pocket_d / 2, -1, p.pocket_depth + 1)
        plate = plate.cut(pocket)
    rim = _ellipse(a, b, zf, zt - zf).cut(_ellipse(ia, ib, zf - 1, zt - zf + 2))
    black = plate.union(rim)

    # --- fields -----------------------------------------------------------------------
    inner_field = _ellipse(ia, ib, zf, p.color_layer)
    band = _slab(cq.Workplane("XY").rect(2 * a, 2 * p.band_half_height), zf, p.color_layer)
    blue = inner_field.intersect(band)
    orange = inner_field.cut(band)

    # --- text -------------------------------------------------------------------------
    first, last = p.first_name.upper(), p.last_name.upper()
    name_specs = [(first, 16.0, 3.4), (last, 8.0, -7.4)]
    white: cq.Workplane | None = None
    for txt, size, y in name_specs:
        t = _text(p, txt, size, 0, y, zr, hn)
        white = t if white is None else white.union(t)
    assert white is not None
    black_specs = [  # symmetric head block (centred on x = 0)
        (p.org, 11.0, 25.0),
        (p.title, 5.2, 16.4),
        (p.location, 5.0, -17.4),
        (p.id_display, 9.0, -25.2),
    ]
    black_text: cq.Workplane | None = None
    for txt, size, y in black_specs:
        t = _text(p, txt, size, 0, y, zr, h)
        black_text = t if black_text is None else black_text.union(t)
    assert black_text is not None

    # --- engraved drop shadow (lower right): shifted text copy minus text footprint.
    # name: full depth down to the black plate (strong contrast on blue);
    # small black text on orange: shallow 0.4 mm groove (shape only, no colour smear)
    dx, dy = p.shadow_offset, -p.shadow_offset
    for txt, size, y in name_specs:
        foot = _text(p, txt, size, 0, y, zf, p.color_layer)
        blue = blue.cut(foot.translate((dx, dy, 0)).cut(foot))
    shallow = p.color_layer / 2
    for txt, size, y in black_specs:
        foot = _text(p, txt, size, 0, y, zf + shallow, shallow)
        orange = orange.cut(foot.translate((dx * 0.7, dy * 0.7, 0)).cut(foot))

    # --- hops (left) and barley (right), mirrored about x = 0 ----------------------------
    sx_pos, sy_pos, scale = 28.0, 13.2, 0.78
    hop_sil, hop_arcs = _hop(-sx_pos, sy_pos, scale, zr, h)
    hop_fill = hop_sil.cut(hop_arcs.translate((0, 0, h / 2)))
    barley, awns = _barley(sx_pos, sy_pos, scale, zr, h)
    black_syms = _outline(hop_sil, 0.6, h).union(_outline(barley, 0.6, h)).union(awns)
    amber = hop_fill.union(barley)

    return {
        "black": black.union(black_text).union(black_syms),
        "orange": orange,
        "blue": blue,
        "white": white,
        "amber": amber,
        "counterplate": build_counterplate(p).translate((0, -(b + 14.0), 0)),
    }


def build_counterplate(p: BadgeParams) -> cq.Workplane:
    """Plate worn inside the shirt; magnets sit in pockets facing the fabric (print pocket-down)."""
    plate = _rrect(p.plate_w, p.plate_h, 3.0, 0, 0, 0, p.plate_t)
    for sx in (-1, 1):
        pocket = _circle(sx * p.magnet_spacing / 2, 0, p.pocket_d / 2, -1, p.pocket_depth + 1)
        plate = plate.cut(pocket)
    return plate.faces(">Z").edges().fillet(0.6)


def check_fit(p: BadgeParams, solids: Solids) -> list[str]:
    """Relief must lie inside the inner ellipse shrunk by edge_clearance and must not
    collide with other-coloured relief. Returns a list of problems."""
    problems: list[str] = []
    big = cq.Workplane("XY").box(400, 400, 5, centered=(True, True, False))
    relief_zone = big.translate((0, 0, p.z_relief))
    limit = _ellipse(p.inner_a - p.edge_clearance, p.inner_b - p.edge_clearance, p.z_relief - 1, 9)
    inside = _ellipse(p.inner_a - 0.01, p.inner_b - 0.01, p.z_relief - 1, 9)
    relief: Solids = {}
    for name in ("black", "white", "amber"):
        feat = solids[name].intersect(relief_zone).intersect(inside)
        relief[name] = feat
        outside = feat.cut(limit)
        vol = outside.val().Volume() if outside.vals() else 0.0
        if vol > 0.02:
            problems.append(f"{name}: relief within {p.edge_clearance} mm of rim ({vol:.2f} mm3)")
    names = list(relief)
    for i, n1 in enumerate(names):
        for n2 in names[i + 1 :]:
            inter = relief[n1].intersect(relief[n2])
            vol = inter.val().Volume() if inter.vals() else 0.0
            if vol > 0.01:
                problems.append(f"overlap {n1}/{n2}: {vol:.3f} mm3")
    return problems


# ---------------------------------------------------------------- export ------------
def _mesh(wp: cq.Workplane, tol: float = 0.01) -> tuple[list, list]:
    """Tessellate and weld coincident vertices (per-face tessellation duplicates them)."""
    verts, tris = wp.val().tessellate(tol, 0.2)
    index: dict[tuple[int, int, int], int] = {}
    out_v: list[tuple[float, float, float]] = []
    remap: list[int] = []
    for v in verts:
        key = (round(v.x * 1e4), round(v.y * 1e4), round(v.z * 1e4))
        if key not in index:
            index[key] = len(out_v)
            out_v.append((v.x, v.y, v.z))
        remap.append(index[key])
    out_t = [(remap[a], remap[b], remap[c]) for a, b, c in tris]
    return out_v, [t for t in out_t if len(set(t)) == 3]


def write_3mf(path: Path, solids: Solids, p: BadgeParams) -> None:
    """Minimal 3MF (mm) with one object per colour and a basematerials group."""
    names = list(solids)
    mats = "".join(f'<base name="{n}" displaycolor="{p.colors[n].upper()}FF"/>' for n in names)
    objs, items = [], []
    for i, n in enumerate(names, start=2):
        v, t = _mesh(solids[n])
        vx = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in v)
        tr = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t)
        objs.append(
            f'<object id="{i}" name="{n}" type="model" pid="1" pindex="{i - 2}">'
            f"<mesh><vertices>{vx}</vertices><triangles>{tr}</triangles></mesh></object>"
        )
        items.append(f'<item objectid="{i}"/>')
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{ns}">'
        '<metadata name="Title">BJCP judge badge (personal use)</metadata>'
        f'<resources><basematerials id="1">{mats}</basematerials>{"".join(objs)}</resources>'
        f"<build>{''.join(items)}</build></model>"
    )
    pkg = "http://schemas.openxmlformats.org/package/2006"
    ct = (
        f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="{pkg}/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" '
        'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    )
    rels = (
        f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{pkg}/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def export_all(
    p: BadgeParams, solids: Solids, out: Path, date: str, material: str = "PLA"
) -> list[Path]:
    for sub in ("step", "stl", "3mf"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    tag = f"EXP_FDM_{material}_{date}"
    asm = cq.Assembly(name="bjcp-badge")
    for n, wp in solids.items():
        r, g, bl = (int(p.colors[n][i : i + 2], 16) / 255 for i in (1, 3, 5))
        asm.add(wp, name=n, color=cq.Color(r, g, bl))
        f = out / "stl" / f"BJCP_badge-{n}_{tag}.stl"
        cq.exporters.export(wp, str(f), tolerance=0.01, angularTolerance=0.2)
        written.append(f)
    step = out / "step" / f"BJCP_badge_{tag}.step"
    asm.export(str(step), "STEP")
    written.append(step)
    f3 = out / "3mf" / f"BJCP_badge_{tag}.3mf"
    write_3mf(f3, solids, p)
    written.append(f3)
    return written


def main() -> int:
    d = BadgeParams()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--first-name", default=d.first_name)
    ap.add_argument("--last-name", default=d.last_name)
    ap.add_argument("--bjcp-id", default=d.bjcp_id)
    ap.add_argument("--location", default=d.location)
    ap.add_argument("--material", default="PLA")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ns = ap.parse_args()
    p = replace(
        d,
        first_name=ns.first_name,
        last_name=ns.last_name,
        bjcp_id=ns.bjcp_id,
        location=ns.location,
    )
    solids = build(p)
    problems = check_fit(p, solids)
    for msg in problems:
        print("FIT PROBLEM:", msg)
    for f in export_all(p, solids, ns.out, ns.date, ns.material):
        print("wrote", f)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
