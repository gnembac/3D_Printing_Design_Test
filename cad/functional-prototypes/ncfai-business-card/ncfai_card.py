"""Generate the NCFAI full-colour 3D-printed business card (single shell, textured OBJ + STL).

Outputs (into --out, filenames follow the project convention):
  <stem>.stl              geometry only, binary, one watertight shell (DFM check / fallback)
  <stem>_obj-package.zip  OBJ + MTL + 2 PNG textures (front / back) = full-colour carrier
  <stem>_preview.png      flat preview of both faces incl. outline and holes
  <stem>.step             only if `cadquery` is installed (parametric master geometry)

The card text lives in a JSON file (personal data -> keep it outside git, see
card_content.example.json). Usage (needs numpy, pillow, shapely, mapbox-earcut, trimesh):

    python ncfai_card.py --content private/ncfai-business-card/card_content.json \
        --logo private/ncfai-business-card/ncfai_logo.png --out private/ncfai-business-card \
        --date 2026-10-09
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from card_params import (  # noqa: E402
    Bubble,
    CardParams,
    layout_bubbles,
    min_ligament,
    seed_int,
    seed_tag,
)

# Colours sampled from the NCFAI logo (`estimated`, sRGB; process colour will differ)
ORANGE = (253, 138, 36)
PURPLE = (62, 67, 138)
BLUE = (20, 115, 192)
NAVY = (27, 42, 107)  # text colour (`estimated`)
FONT_BOLD = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)
PRINT_MARGIN = 1.5  # keep ink away from the card edge (colour/geometry registration `ASSUMPTION`)
RING_GAP, RING_W = 0.6, 0.9  # colour ring around each hole, mm
MIN_STROKE = 0.4  # smallest printed colour stroke, mm (`ASSUMPTION`, verify with supplier)


@dataclass(frozen=True)
class CardContent:
    name: str
    company: str
    qualification: str
    address: tuple[str, ...]

    @staticmethod
    def load(path: Path) -> CardContent:
        d = json.loads(path.read_text(encoding="utf-8"))
        return CardContent(d["name"], d["company"], d["qualification"], tuple(d["address"]))


def lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def gradient(t: float) -> tuple[int, int, int]:
    """Logo gradient orange -> purple -> blue, t in 0..1."""
    t = min(1.0, max(0.0, t))
    return lerp(ORANGE, PURPLE, t * 2) if t < 0.5 else lerp(PURPLE, BLUE, (t - 0.5) * 2)


def font(size_mm: float, ppmm: float) -> ImageFont.FreeTypeFont:
    for f in FONT_BOLD:
        if Path(f).exists():
            return ImageFont.truetype(f, round(size_mm * ppmm))
    raise FileNotFoundError("no bold sans font found (Liberation Sans / DejaVu Sans)")


def trim_logo(img: Image.Image) -> Image.Image:
    """Flatten transparency onto white (alpha -> black otherwise) and crop to the artwork."""
    rgba = img.convert("RGBA")
    flat = Image.new("RGB", rgba.size, (255, 255, 255))
    flat.paste(rgba, mask=rgba.getchannel("A"))
    ys, xs = np.where(np.asarray(flat).min(axis=2) < 225)
    return flat.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def rounded_mask_polygon(p: CardParams, bubbles: list[Bubble]) -> Polygon:
    """Card outline in card coordinates (y down) incl. holes - used for the preview."""
    outer = box(0, 0, p.width, p.height).buffer(-p.corner_r).buffer(p.corner_r, quad_segs=24)
    holes = [Point(b.x, b.y).buffer(b.d / 2, quad_segs=24) for b in bubbles]
    for h in holes:
        outer = outer.difference(h)
    return outer


def _px(v: float, ppmm: float) -> int:
    return round(v * ppmm)


def _draw_rings(
    draw: ImageDraw.ImageDraw, bubbles: list[Bubble], p: CardParams, ppmm: float, mirror: bool
) -> None:
    for b in bubbles:
        x = p.width - b.x if mirror else b.x
        for r_out, r_in in ((b.d / 2 + RING_GAP + RING_W, b.d / 2 + RING_GAP),):
            box_ = [_px(x - r_out, ppmm), _px(b.y - r_out, ppmm)]
            box2 = [_px(x + r_out, ppmm), _px(b.y + r_out, ppmm)]
            draw.ellipse([*box_, *box2], fill=gradient(x / p.width))
            ri = [
                _px(x - r_in, ppmm),
                _px(b.y - r_in, ppmm),
                _px(x + r_in, ppmm),
                _px(b.y + r_in, ppmm),
            ]
            draw.ellipse(ri, fill=(255, 255, 255))


def render_front(
    p: CardParams, c: CardContent, logo: Image.Image, bubbles: list[Bubble], ppmm: float
) -> Image.Image:
    img = Image.new("RGB", (_px(p.width, ppmm), _px(p.height, ppmm)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # logo, top-left, width 31 mm
    lw = 31.0
    lh = lw * logo.height / logo.width
    big = logo.resize((_px(lw, ppmm), _px(lh, ppmm)), Image.LANCZOS)
    img.paste(big, (_px(5.0, ppmm), _px(5.0, ppmm)))
    # name, two lines right of the logo
    first, _, last = c.name.partition(" ")
    fn = font(7.2, ppmm)
    d.text((_px(41.0, ppmm), _px(5.0, ppmm)), first, font=fn, fill=NAVY)
    d.text((_px(41.0, ppmm), _px(5.0 + 8.4, ppmm)), last, font=fn, fill=NAVY)
    # gradient rule
    y0, y1 = _px(24.6, ppmm), _px(24.6 + 0.6, ppmm)
    for x in range(_px(5.0, ppmm), _px(p.width - 5.0, ppmm)):
        d.line([(x, y0), (x, y1)], fill=gradient((x / ppmm - 5.0) / (p.width - 10.0)))
    # company + qualification
    f2 = font(2.9, ppmm)
    d.text((_px(5.0, ppmm), _px(27.0, ppmm)), c.company, font=f2, fill=NAVY)
    d.text((_px(5.0, ppmm), _px(31.2, ppmm)), c.qualification, font=f2, fill=NAVY)
    # address block bottom-left
    f3 = font(2.6, ppmm)
    for i, line in enumerate(c.address):
        d.text((_px(5.0, ppmm), _px(38.0 + 3.7 * i, ppmm)), line, font=f3, fill=NAVY)
    _draw_rings(d, bubbles, p, ppmm, mirror=False)
    return img


def render_back(p: CardParams, c: CardContent, bubbles: list[Bubble], ppmm: float) -> Image.Image:
    """Back face as seen from behind (mirrored x). Seeded bubble foam + unique ID label."""
    img = Image.new("RGB", (_px(p.width, ppmm), _px(p.height, ppmm)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    rng = random.Random(seed_int(p.seed) + 1)
    holes = [(p.width - b.x, b.y, b.d / 2 + RING_GAP + RING_W) for b in bubbles]
    label = (14.0, 19.0, p.width - 14.0, 36.0)
    placed: list[tuple[float, float, float]] = []
    for _ in range(1500):
        r = rng.choice((0.9, 1.2, 1.6, 2.2, 3.0, 4.2)) * rng.uniform(0.85, 1.15)
        x = rng.uniform(PRINT_MARGIN + r, p.width - PRINT_MARGIN - r)
        y = rng.uniform(PRINT_MARGIN + r, p.height - PRINT_MARGIN - r)
        if any(math.hypot(x - hx, y - hy) < hr + r + 0.8 for hx, hy, hr in holes):
            continue
        if label[0] - r < x < label[2] + r and label[1] - r < y < label[3] + r:
            continue
        if any(math.hypot(x - ox, y - oy) < (or_ + r) * 0.8 for ox, oy, or_ in placed):
            continue
        # keep the bubble inside the rounded outline
        if not _inside_outline(p, x, y, r + PRINT_MARGIN, mirror=True):
            continue
        placed.append((x, y, r))
    for x, y, r in placed:
        col = gradient(x / p.width + rng.uniform(-0.08, 0.08))
        d.ellipse(
            [_px(x - r, ppmm), _px(y - r, ppmm), _px(x + r, ppmm), _px(y + r, ppmm)], fill=col
        )
        if r >= 1.5:  # highlight -> reads as bubble
            hr = r * 0.32
            hx, hy = x - r * 0.35, y - r * 0.35
            d.ellipse(
                [_px(hx - hr, ppmm), _px(hy - hr, ppmm), _px(hx + hr, ppmm), _px(hy + hr, ppmm)],
                fill=lerp(col, (255, 255, 255), 0.65),
            )
    _draw_rings(d, bubbles, p, ppmm, mirror=True)
    # label with unique ID
    lx0, ly0, lx1, ly1 = (_px(v, ppmm) for v in label)
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=_px(2.0, ppmm), fill=(255, 255, 255))
    cx = _px(p.width / 2, ppmm)
    for text, size, y in (
        ("UNIKAT", 5.4, 20.4),
        (f"No. {seed_tag(p.seed)}", 3.0, 27.0),
    ):
        f = font(size, ppmm)
        w = d.textlength(text, font=f)
        d.text((cx - w / 2, _px(y, ppmm)), text, font=f, fill=NAVY)
    f = font(2.4, ppmm)
    w = d.textlength(c.company, font=f)
    d.text((cx - w / 2, _px(31.8, ppmm)), c.company, font=f, fill=NAVY)
    return img


def _inside_outline(p: CardParams, x: float, y: float, r: float, mirror: bool) -> bool:
    """True if a circle (x, y, r) in image coordinates lies inside the rounded card outline."""
    xx = p.width - x if mirror else x
    cx = min(max(xx, p.corner_r), p.width - p.corner_r)
    cy = min(max(y, p.corner_r), p.height - p.corner_r)
    if (xx, y) == (cx, cy):  # not in a corner zone
        return min(xx, p.width - xx, y, p.height - y) >= r
    return math.hypot(xx - cx, y - cy) + r <= p.corner_r


def outline_polygon(p: CardParams, bubbles: list[Bubble]) -> Polygon:
    """Card outline centred on the origin, y up, CCW exterior / CW holes (mesh coordinates)."""
    n = max(8, math.ceil((math.pi / 2) / math.acos(1 - p.arc_tol / p.corner_r)))
    outer = (
        box(-p.width / 2, -p.height / 2, p.width / 2, p.height / 2)
        .buffer(-p.corner_r)
        .buffer(p.corner_r, quad_segs=n)
    )
    for b in bubbles:
        nh = max(8, math.ceil((math.pi / 2) / math.acos(1 - p.arc_tol / (b.d / 2))))
        hole = Point(b.x - p.width / 2, p.height / 2 - b.y).buffer(b.d / 2, quad_segs=nh)
        outer = outer.difference(hole)
    return orient(outer, 1.0)


@dataclass
class CardMesh:
    verts: np.ndarray  # (n, 3) all vertices (top, bottom, side)
    uv: np.ndarray  # (2n_top, 2): vt for top [0:n_top] and bottom [n_top:]
    top_faces: np.ndarray
    bottom_faces: np.ndarray
    side_faces: np.ndarray
    n_top: int

    def geometry(self) -> trimesh.Trimesh:
        faces = np.vstack([self.top_faces, self.bottom_faces, self.side_faces])
        m = trimesh.Trimesh(self.verts.copy(), faces, process=True)
        m.merge_vertices()
        return m


def build_mesh(p: CardParams, bubbles: list[Bubble]) -> CardMesh:
    poly = outline_polygon(p, bubbles)
    v2, f = trimesh.creation.triangulate_polygon(poly, engine="earcut")
    v2 = np.asarray(v2, dtype=float)
    f = np.asarray(f)
    a, b, c = v2[f[:, 0]], v2[f[:, 1]], v2[f[:, 2]]
    cross = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    f = np.where((cross < 0)[:, None], f[:, ::-1], f)  # all CCW -> normal +z on top
    n = len(v2)
    t = p.thickness
    top = np.column_stack([v2, np.full(n, t)])
    bot = np.column_stack([v2, np.zeros(n)])
    side_v: list[np.ndarray] = []
    side_f: list[list[int]] = []
    base = 2 * n
    for ring in (poly.exterior, *poly.interiors):
        pts = np.asarray(ring.coords)[:-1]
        for i in range(len(pts)):
            q0, q1 = pts[i], pts[(i + 1) % len(pts)]
            side_v += [
                [q0[0], q0[1], 0.0],
                [q1[0], q1[1], 0.0],
                [q1[0], q1[1], t],
                [q0[0], q0[1], t],
            ]
            side_f += [[base, base + 1, base + 2], [base, base + 2, base + 3]]
            base += 4
    verts = np.vstack([top, bot, np.asarray(side_v)])
    u_front = (v2[:, 0] + p.width / 2) / p.width
    u_back = (p.width / 2 - v2[:, 0]) / p.width
    vv = (v2[:, 1] + p.height / 2) / p.height
    uv = np.vstack([np.column_stack([u_front, vv]), np.column_stack([u_back, vv])])
    return CardMesh(verts, uv, f, f[:, ::-1] + n, np.asarray(side_f), n)


def write_obj_package(
    path: Path,
    m: CardMesh,
    front: Image.Image,
    back: Image.Image,
    ppmm: float,
    dpi_note: str,
) -> None:
    stem = "ncfai-card"
    lines = [f"# {dpi_note}", f"mtllib {stem}.mtl", f"o {stem}"]
    lines += [f"v {x:.5f} {y:.5f} {z:.5f}" for x, y, z in m.verts]
    lines += [f"vt {u:.6f} {v:.6f}" for u, v in m.uv]
    n = m.n_top
    lines.append("usemtl front")
    lines += [f"f {a + 1}/{a + 1} {b + 1}/{b + 1} {c + 1}/{c + 1}" for a, b, c in m.top_faces]
    lines.append("usemtl back")
    lines += [f"f {a + 1}/{a + 1} {b + 1}/{b + 1} {c + 1}/{c + 1}" for a, b, c in m.bottom_faces]
    lines.append("usemtl edge")
    lines += [f"f {a + 1} {b + 1} {c + 1}" for a, b, c in m.side_faces]
    del n

    def mtl(name: str, tex: str | None) -> list[str]:
        out = [f"newmtl {name}", "Ka 1 1 1", "Kd 1 1 1", "Ks 0 0 0", "d 1", "illum 1"]
        return out + ([f"map_Kd {tex}"] if tex else []) + [""]

    mtl_txt = "\n".join(
        mtl("front", f"{stem}_front.png") + mtl("back", f"{stem}_back.png") + mtl("edge", None)
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{stem}.obj", "\n".join(lines) + "\n")
        z.writestr(f"{stem}.mtl", mtl_txt)
        for name, img in ((f"{stem}_front.png", front), (f"{stem}_back.png", back)):
            tmp = path.with_suffix(f".{name}.tmp")
            img.save(tmp, "PNG", dpi=(ppmm * 25.4, ppmm * 25.4), optimize=True)
            z.write(tmp, name)
            tmp.unlink()


def write_preview(
    path: Path, p: CardParams, front: Image.Image, back: Image.Image, bubbles: list[Bubble]
) -> None:
    scale = 1000 / p.width  # px per mm
    w, h = round(p.width * scale), round(p.height * scale)
    outline = rounded_mask_polygon(p, bubbles)
    sheet = Image.new("RGB", (w * 2 + 90, h + 60), (214, 220, 230))
    for k, img in enumerate((front, back)):  # back texture is already the view from behind
        small = img.resize((w, h), Image.LANCZOS)
        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        mx = (lambda x: p.width - x) if k else (lambda x: x)
        md.polygon([(mx(x) * scale, y * scale) for x, y in outline.exterior.coords], fill=255)
        for ring in outline.interiors:
            md.polygon([(mx(x) * scale, y * scale) for x, y in ring.coords], fill=0)
        sheet.paste(small, (30 + k * (w + 30), 30), mask)
    sheet.save(path, "PNG", optimize=True)


def write_step(path: Path, p: CardParams, bubbles: list[Bubble]) -> bool:
    try:
        import cadquery as cq
    except ImportError:
        return False
    s = (
        cq.Workplane("XY")
        .box(p.width, p.height, p.thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(p.corner_r)
    )
    for b in bubbles:
        cut = (
            cq.Workplane("XY")
            .center(b.x - p.width / 2, p.height / 2 - b.y)
            .circle(b.d / 2)
            .extrude(p.thickness)
        )
        s = s.cut(cut)
    cq.exporters.export(s, str(path))
    return True


def check(
    p: CardParams, bubbles: list[Bubble], geo: trimesh.Trimesh
) -> list[tuple[str, str, bool]]:
    """(check, result, passed) - screening against supplier values, not a supplier approval."""
    web = min_ligament(p, bubbles)
    dmin = min((b.d for b in bubbles), default=math.inf)
    bb = geo.bounds[1] - geo.bounds[0]
    rows = [
        (
            "Geometry watertight, 1 shell",
            f"{geo.is_watertight}, {len(geo.split())} shell(s)",
            geo.is_watertight and len(geo.split()) == 1,
        ),
        (
            "Winding consistent / volume > 0",
            f"{geo.is_winding_consistent}, {geo.volume:.0f} mm3",
            geo.is_winding_consistent and geo.volume > 0,
        ),
        (
            "Bounding box X x Y x Z",
            f"{bb[0]:.2f} x {bb[1]:.2f} x {bb[2]:.2f} mm",
            abs(bb[0] - p.width) < 1e-3
            and abs(bb[1] - p.height) < 1e-3
            and abs(bb[2] - p.thickness) < 1e-3,
        ),
        (
            "Thickness + tol <= 2.5 mm",
            f"{p.thickness + 0.3:.2f} mm",
            p.thickness + 0.3 <= 2.5 + 1e-9,
        ),
        (
            "Thickness - tol >= 2.0 mm? (informational)",
            f"{p.thickness - 0.3:.2f} mm",
            p.thickness - 0.3 >= 2.0,
        ),
        (
            "Min. web (hole-hole / hole-edge) >= 2.0 mm",
            "k.A." if not bubbles else f"{web:.2f} mm",
            (not bubbles) or web >= 2.0,
        ),
        (
            "Min. hole diameter >= 1.5 mm (+ tol)",
            "k.A." if not bubbles else f"{dmin:.1f} mm",
            (not bubbles) or dmin >= 1.5 + 2 * 0.3,
        ),
    ]
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--content", type=Path, required=True)
    ap.add_argument("--logo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD for the filename")
    ap.add_argument("--seed", default=None, help="unique-card seed (default from card_params)")
    ap.add_argument("--bubbles", type=int, default=None, help="0 = flat control variant")
    ap.add_argument("--part-number", default="unikat001")
    ap.add_argument(
        "--ppmm", type=float, default=40.0, help="texture pixels per mm (40 = 1016 dpi)"
    )
    a = ap.parse_args()

    p = CardParams()
    if a.seed is not None:
        p = replace(p, seed=a.seed)
    if a.bubbles is not None:
        p = replace(p, n_bubbles=a.bubbles)
    bubbles = layout_bubbles(p)
    content = CardContent.load(a.content)
    logo = trim_logo(Image.open(a.logo))

    a.out.mkdir(parents=True, exist_ok=True)
    part = a.part_number + ("" if bubbles else "-flat")
    stem = f"NCFAI-card_{part}_EXP_MJF_PAC-HP_{a.date}"

    front = render_front(p, content, logo, bubbles, a.ppmm)
    back = render_back(p, content, bubbles, a.ppmm)
    mesh = build_mesh(p, bubbles)
    geo = mesh.geometry()

    geo.export(a.out / f"{stem}.stl")
    write_obj_package(
        a.out / f"{stem}_obj-package.zip",
        mesh,
        front,
        back,
        a.ppmm,
        f"NCFAI card, seed tag {seed_tag(p.seed)}, units mm, texture {a.ppmm:g} px/mm",
    )
    write_preview(a.out / f"{stem}_preview.png", p, front, back, bubbles)
    step_ok = write_step(a.out / f"{stem}.step", p, bubbles)

    rows = check(p, bubbles, geo)
    print(f"seed={p.seed} tag={seed_tag(p.seed)} bubbles={len(bubbles)}")
    for b in bubbles:
        print(f"  bubble x={b.x:6.2f} y={b.y:6.2f} d={b.d:.1f}")
    for name, res, ok in rows:
        info = "informational" in name
        print(f"[{'PASS' if ok else ('INFO' if info else 'FAIL')}] {name}: {res}")
    print(f"STEP: {'written' if step_ok else 'skipped (cadquery not installed)'}")
    print(f"files: {a.out}/{stem}*")
    return 0 if all(ok for n, _, ok in rows if "informational" not in n) else 1


if __name__ == "__main__":
    raise SystemExit(main())
