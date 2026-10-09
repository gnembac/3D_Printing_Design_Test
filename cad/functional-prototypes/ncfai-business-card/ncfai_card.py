"""Generate the NCFAI full-colour 3D-printed business card (single shell, textured OBJ + STL).

Geometry: base plate 2.0 mm + 0.5 mm relief on the front (raised name, hop cone, badges with
ENGRAVED lettering; engraving cuts down to the base plane, never below). Back is flat + QR code.

Outputs (into --out, filenames follow the project convention):
  <stem>.stl              geometry only, binary, one watertight shell (DFM check / fallback)
  <stem>_obj-package.zip  OBJ + MTL + 2 PNG textures (front / back) = full-colour carrier
  <stem>_preview.png      preview: front (with relief shading) and back
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
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
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
from card_qr import QrLayout, make_layout  # noqa: E402
from card_relief import (  # noqa: E402
    FrontRelief,
    badge_layout,
    build_front_relief,
    parts,
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
QR_DARK = (0, 0, 0)  # K black: max. contrast (supplier colour mapping `k.A.`)
QR_RIGHT, QR_TOP = 7.0, 7.0  # module area: distance from right edge / top, mm
GREEN_FLOOR = (38, 94, 30)  # hop cone groove floor (`estimated`)
GREEN_TOP, GREEN_BOT = (160, 207, 66), (56, 140, 46)  # bract colours top -> tip (`estimated`)
MIN_STROKE = 0.4  # smallest printed colour stroke, mm (`ASSUMPTION`, verify with supplier)


@dataclass(frozen=True)
class CardContent:
    name: str
    company: str
    qualification: str
    address: tuple[str, ...]
    url: str = ""
    badges: tuple[tuple[str, str], ...] = ()  # (engraved word, caption below)

    @staticmethod
    def load(path: Path) -> CardContent:
        d = json.loads(path.read_text(encoding="utf-8"))
        return CardContent(
            d["name"],
            d["company"],
            d["qualification"],
            tuple(d["address"]),
            d.get("url", ""),
            tuple((w, cap) for w, cap in d.get("badges", [])),
        )


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


def _paint(
    draw: ImageDraw.ImageDraw,
    geom: BaseGeometry,
    fill: tuple[int, int, int],
    ppmm: float,
    hole: tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Fill shapely geometry (card coordinates, mm) into the texture; larger shapes first."""
    for poly in sorted(parts(geom), key=lambda q: -q.area):
        draw.polygon([(x * ppmm, y * ppmm) for x, y in poly.exterior.coords], fill=fill)
        for ring in poly.interiors:
            draw.polygon([(x * ppmm, y * ppmm) for x, y in ring.coords], fill=hole)


def render_front(
    p: CardParams,
    c: CardContent,
    logo: Image.Image,
    bubbles: list[Bubble],
    ppmm: float,
    relief: FrontRelief,
) -> Image.Image:
    img = Image.new("RGB", (_px(p.width, ppmm), _px(p.height, ppmm)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # logo, top-left, width 31 mm
    lw = 31.0
    lh = lw * logo.height / logo.width
    big = logo.resize((_px(lw, ppmm), _px(lh, ppmm)), Image.LANCZOS)
    img.paste(big, (_px(5.0, ppmm), _px(5.0, ppmm)))
    # gradient rule (flat colour, base level)
    y0, y1 = _px(23.9, ppmm), _px(23.9 + 0.6, ppmm)
    for x in range(_px(5.0, ppmm), _px(p.width - 5.0, ppmm)):
        d.line([(x, y0), (x, y1)], fill=gradient((x / ppmm - 5.0) / (p.width - 10.0)))
    # flat (printed, no relief) small text: strokes too thin for 0.8 mm relief
    f2 = font(2.9, ppmm)
    d.text((_px(5.0, ppmm), _px(26.2, ppmm)), c.company, font=f2, fill=NAVY)
    f3 = font(2.6, ppmm)
    if c.badges:
        for (_, cap), (x0, _) in zip(
            c.badges, badge_layout(tuple(w for w, _ in c.badges)), strict=True
        ):
            d.text((_px(x0 + 1.0, ppmm), _px(38.6, ppmm)), cap, font=f3, fill=NAVY)
    else:
        d.text((_px(5.0, ppmm), _px(31.2, ppmm)), c.qualification, font=f2, fill=NAVY)
    for i, line in enumerate(c.address):
        d.text((_px(5.0, ppmm), _px(42.4 + 3.4 * i, ppmm)), line, font=f3, fill=NAVY)
    # hop cone: groove floor (base level) dark green, bracts (raised) lighter green
    _paint(d, relief.cone.silhouette, GREEN_FLOOR, ppmm)
    for tile, t in relief.cone.tiles:
        _paint(d, tile, lerp(GREEN_TOP, GREEN_BOT, t), ppmm)
    _paint(d, relief.cone.stalk, lerp(GREEN_TOP, GREEN_BOT, 0.3), ppmm)
    # raised name + badges (engraved letters = white base plane showing through)
    _paint(d, relief.name, NAVY, ppmm)
    _paint(d, relief.badges, NAVY, ppmm)
    _draw_rings(d, bubbles, p, ppmm, mirror=False)
    return img


def render_back(
    p: CardParams, c: CardContent, logo: Image.Image, bubbles: list[Bubble], ppmm: float
) -> Image.Image:
    """Back face as seen from behind (not mirrored: this is the picture the viewer sees).

    Left column: unique ID + foam bubbles around the hole rings; right: large QR code (c.url).
    """
    img = Image.new("RGB", (_px(p.width, ppmm), _px(p.height, ppmm)), (255, 255, 255))
    d = ImageDraw.Draw(img)
    rng = random.Random(seed_int(p.seed) + 1)
    holes = [(p.width - b.x, b.y, b.d / 2 + RING_GAP + RING_W) for b in bubbles]
    keep: list[tuple[float, float, float, float]] = [(4.0, 4.0, 38.5, 34.0)]  # logo + ID text
    qr = None
    if c.url:
        qr = make_layout(c.url, p.width - QR_RIGHT, QR_TOP, ppmm)
        qx0, qy0, qx1, qy1 = qr.keep_out
        keep += [(qx0, qy0, qx1, qy1), (qx0, qy1, qx1, qy1 + 8.0)]  # quiet zone + caption
        for hx, hy, hr in holes:  # rings are ink: they must not touch the quiet zone
            if hx + hr > qx0 - 0.5 and hy + hr > qy0 and hy - hr < qy1 + 8.0:
                raise ValueError("hole ring intrudes into the QR quiet zone; change seed/layout")
    placed: list[tuple[float, float, float]] = []
    for _ in range(1500):
        r = rng.choice((0.9, 1.2, 1.6, 2.2, 3.0, 4.2)) * rng.uniform(0.85, 1.15)
        x = rng.uniform(PRINT_MARGIN + r, p.width - PRINT_MARGIN - r)
        y = rng.uniform(PRINT_MARGIN + r, p.height - PRINT_MARGIN - r)
        if any(math.hypot(x - hx, y - hy) < hr + r + 0.8 for hx, hy, hr in holes):
            continue
        if any(
            k[0] - r - 0.5 < x < k[2] + r + 0.5 and k[1] - r - 0.5 < y < k[3] + r + 0.5
            for k in keep
        ):
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
    # logo (replaces the former text block) + unique ID
    lw = 33.0
    lh = lw * logo.height / logo.width
    img.paste(
        logo.resize((_px(lw, ppmm), _px(lh, ppmm)), Image.LANCZOS), (_px(5.0, ppmm), _px(5.0, ppmm))
    )
    d.text((_px(5.0, ppmm), _px(5.0 + lh + 2.6, ppmm)), "UNIKAT", font=font(3.6, ppmm), fill=NAVY)
    d.text(
        (_px(5.0, ppmm), _px(5.0 + lh + 7.0, ppmm)),
        f"No. {seed_tag(p.seed)}",
        font=font(2.8, ppmm),
        fill=NAVY,
    )
    if qr is not None:
        m = qr.module_mm
        for r_i, row in enumerate(qr.matrix):
            for c_i, dark in enumerate(row):
                if dark:
                    x0, y0 = _px(qr.x + c_i * m, ppmm), _px(qr.y + r_i * m, ppmm)
                    d.rectangle(
                        [x0, y0, x0 + _px(m, ppmm) - 1, y0 + _px(m, ppmm) - 1], fill=QR_DARK
                    )
        cap = c.url.removeprefix("https://").removeprefix("http://").rstrip("/")
        fc = font(2.8, ppmm)
        w = d.textlength(cap, font=fc)
        cx = qr.x + qr.size / 2
        d.text((_px(cx, ppmm) - w / 2, _px(qr.keep_out[3] + 0.4, ppmm)), cap, font=fc, fill=NAVY)
    return img


def verify_qr(back: Image.Image, qr: QrLayout, url: str, ppmm: float) -> list[tuple[str, bool]]:
    """Decode the rendered texture, also after simulated blur and ink spread (`estimated`)."""
    try:
        import zxingcpp
    except ImportError:
        return []
    x0, y0, x1, y1 = (_px(v, ppmm) for v in qr.keep_out)
    crop = back.crop((x0, y0, x1, y1)).convert("L")
    out = []
    cases = {
        "as rendered": crop,
        "blur 0.25 mm": crop.filter(ImageFilter.GaussianBlur(0.25 * ppmm)),
        "ink spread +0.10 mm/side": crop.filter(ImageFilter.MinFilter(2 * round(0.10 * ppmm) + 1)),
        "ink loss -0.10 mm/side": crop.filter(ImageFilter.MaxFilter(2 * round(0.10 * ppmm) + 1)),
        "scan at 8 px/mm": crop.resize(
            (round(crop.width / ppmm * 8), round(crop.height / ppmm * 8))
        ),
    }
    for name, im in cases.items():
        res = zxingcpp.read_barcodes(np.asarray(im))
        out.append((name, any(r.text == url for r in res)))
    return out


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
    verts: np.ndarray  # (n, 3)
    uv: np.ndarray  # (n, 2) texture coordinates for every vertex
    groups: dict[str, np.ndarray]  # material (front | back | edge) -> faces

    def geometry(self) -> trimesh.Trimesh:
        faces = np.vstack([f for f in self.groups.values() if len(f)])
        m = trimesh.Trimesh(self.verts.copy(), faces, process=True)
        m.merge_vertices()
        return m


def _tri(poly: Polygon) -> tuple[np.ndarray, np.ndarray]:
    """Earcut triangulation (no Steiner points), all triangles CCW -> normal +z."""
    v2, f = trimesh.creation.triangulate_polygon(poly, engine="earcut")
    v2, f = np.asarray(v2, dtype=float), np.asarray(f)
    a, b, c = v2[f[:, 0]], v2[f[:, 1]], v2[f[:, 2]]
    cross = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    return v2, np.where((cross < 0)[:, None], f[:, ::-1], f)


def _low_regions(outline: Polygon, raised: list[Polygon]) -> list[Polygon]:
    """Base-plane regions = outline minus raised islands, built from the raised rings themselves
    (exact coordinates -> watertight). Supports raised polygons nested in engraved cut-outs."""
    inner = [(Polygon(r), q) for q in raised for r in q.interiors]
    holders = {
        id(q): any(ring.contains(q) for ring, owner in inner if owner is not q) for q in raised
    }
    top = [q for q in raised if not holders[id(q)]]
    regions = [
        orient(
            Polygon(
                outline.exterior.coords,
                [r.coords for r in outline.interiors] + [q.exterior.coords for q in top],
            ),
            1.0,
        )
    ]
    for ring, owner in inner:
        islands = [q for q in raised if q is not owner and ring.contains(q)]
        regions.append(
            orient(Polygon(ring.exterior.coords, [q.exterior.coords for q in islands]), 1.0)
        )
    return regions


def build_mesh(p: CardParams, bubbles: list[Bubble], raised_card: BaseGeometry | None) -> CardMesh:
    """Single shell: bottom z=0, base plane z=base, raised plane z=base+relief (front only)."""
    W, H, zb, zt = p.width, p.height, p.base_thickness, p.total_thickness
    outline = outline_polygon(p, bubbles)
    raised: list[Polygon] = []
    if raised_card is not None and p.relief > 0 and not raised_card.is_empty:
        g = affinity.affine_transform(raised_card, [1, 0, 0, -1, -W / 2, H / 2])
        raised = [orient(q, 1.0) for q in parts(g)]
        keep = outline.buffer(-p.relief_margin)
        if not all(keep.contains(q) for q in raised):
            raise ValueError("raised feature closer than relief_margin to the card edge/hole")
    vs: list[np.ndarray] = []
    us: list[np.ndarray] = []
    groups: dict[str, list[np.ndarray]] = {"front": [], "back": [], "edge": []}
    count = [0]

    def uv_front(xy: np.ndarray) -> np.ndarray:
        return np.column_stack([(xy[:, 0] + W / 2) / W, (xy[:, 1] + H / 2) / H])

    def uv_back(xy: np.ndarray) -> np.ndarray:
        return np.column_stack([(W / 2 - xy[:, 0]) / W, (xy[:, 1] + H / 2) / H])

    def add(v3: np.ndarray, uv: np.ndarray, faces: np.ndarray, mat: str) -> None:
        vs.append(v3)
        us.append(uv)
        groups[mat].append(faces + count[0])
        count[0] += len(v3)

    def face(poly: Polygon, z: float, mat: str, uvf, flip: bool = False) -> None:  # noqa: ANN001
        v2, f = _tri(poly)
        add(np.column_stack([v2, np.full(len(v2), z)]), uvf(v2), f[:, ::-1] if flip else f, mat)

    def walls(poly: Polygon, z0: float, z1: float, mat: str, uvf) -> None:  # noqa: ANN001
        for ring in (poly.exterior, *poly.interiors):
            pts = np.asarray(ring.coords)[:-1]
            nxt = np.roll(pts, -1, axis=0)
            m = len(pts)
            xy = np.stack([pts, nxt, nxt, pts], axis=1).reshape(-1, 2)  # 4 vertices per segment
            z = np.tile([z0, z0, z1, z1], m)
            k = np.arange(m)[:, None] * 4
            f = np.concatenate([k + [0, 1, 2], k + [0, 2, 3]]).reshape(-1, 3)
            add(np.column_stack([xy, z]), uvf(xy), f, mat)

    for q in parts(outline):
        face(q, 0.0, "back", uv_back, flip=True)
        walls(q, 0.0, zb, "edge", uv_front)
    low = _low_regions(outline, raised) if raised else parts(outline)
    for q in low:
        face(q, zb, "front", uv_front)
    for q in raised:
        face(q, zt, "front", uv_front)
        walls(q, zb, zt, "front", uv_front)  # wall colour = texture colour at the rim
    return CardMesh(
        np.vstack(vs),
        np.vstack(us),
        {k: np.vstack(v) if v else np.empty((0, 3), int) for k, v in groups.items()},
    )


def write_obj_package(
    path: Path, m: CardMesh, front: Image.Image, back: Image.Image, ppmm: float, note: str
) -> None:
    stem = "ncfai-card"
    lines = [f"# {note}", f"mtllib {stem}.mtl", f"o {stem}"]
    lines += [f"v {x:.5f} {y:.5f} {z:.5f}" for x, y, z in m.verts]
    lines += [f"vt {u:.6f} {v:.6f}" for u, v in m.uv]
    for mat in ("front", "back", "edge"):
        lines.append(f"usemtl {mat}")
        lines += [f"f {a + 1}/{a + 1} {b + 1}/{b + 1} {c + 1}/{c + 1}" for a, b, c in m.groups[mat]]

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


def shade_relief(front: Image.Image, raised: BaseGeometry, ppmm: float) -> Image.Image:
    """Preview only: fake lighting from top-left so raised areas read as relief."""
    mask = Image.new("L", front.size, 0)
    d = ImageDraw.Draw(mask)
    _paint(d, raised, 255, ppmm, hole=0)  # type: ignore[arg-type]
    h = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.12 * ppmm)), dtype=float) / 255
    gy, gx = np.gradient(h)
    lit = -(gx + gy)
    lit = lit / max(np.percentile(np.abs(lit), 99.7), 1e-9)
    k = np.clip(1.0 + 0.45 * lit, 0.55, 1.45) * (1.0 + 0.03 * h)
    out = np.clip(np.asarray(front, dtype=float) * k[..., None], 0, 255)
    return Image.fromarray(out.astype("uint8"))


def write_preview(
    path: Path,
    p: CardParams,
    front: Image.Image,
    back: Image.Image,
    bubbles: list[Bubble],
    raised: BaseGeometry,
    ppmm: float,
) -> None:
    scale = 1000 / p.width  # px per mm
    w, h = round(p.width * scale), round(p.height * scale)
    outline = rounded_mask_polygon(p, bubbles)
    sheet = Image.new("RGB", (w * 2 + 90, h + 60), (214, 220, 230))
    front_shaded = shade_relief(front, raised, ppmm) if p.relief > 0 else front
    for k, img in enumerate((front_shaded, back)):  # back texture is already the view from behind
        small = img.resize((w, h), Image.LANCZOS)
        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        mx = (lambda x: p.width - x) if k else (lambda x: x)
        md.polygon([(mx(x) * scale, y * scale) for x, y in outline.exterior.coords], fill=255)
        for ring in outline.interiors:
            md.polygon([(mx(x) * scale, y * scale) for x, y in ring.coords], fill=0)
        sheet.paste(small, (30 + k * (w + 30), 30), mask)
    sheet.save(path, "PNG", optimize=True)


def write_step(
    path: Path, p: CardParams, bubbles: list[Bubble], raised_card: BaseGeometry | None
) -> bool:
    try:
        import cadquery as cq
    except ImportError:
        return False
    s = (
        cq.Workplane("XY")
        .box(p.width, p.height, p.base_thickness, centered=(True, True, False))
        .edges("|Z")
        .fillet(p.corner_r)
    )
    for b in bubbles:
        s = s.cut(
            cq.Workplane("XY")
            .center(b.x - p.width / 2, p.height / 2 - b.y)
            .circle(b.d / 2)
            .extrude(p.base_thickness)
        )
    if raised_card is not None and p.relief > 0:
        g = affinity.affine_transform(raised_card, [1, 0, 0, -1, -p.width / 2, p.height / 2])
        for q in parts(g.simplify(0.01)):
            wp = cq.Workplane("XY").workplane(offset=p.base_thickness)
            wp = wp.polyline(list(q.exterior.coords)[:-1]).close()
            for r in q.interiors:
                wp = wp.polyline(list(r.coords)[:-1]).close()
            s = s.union(wp.extrude(p.relief))
    cq.exporters.export(s, str(path))
    return True


def check(
    p: CardParams, bubbles: list[Bubble], geo: trimesh.Trimesh, rel: FrontRelief
) -> list[tuple[str, str, bool]]:
    """(check, result, passed) - screening against supplier values, not a supplier approval."""
    web = min_ligament(p, bubbles)
    dmin = min((b.d for b in bubbles), default=math.inf)
    bb = geo.bounds[1] - geo.bounds[0]
    n_raised = len(parts(rel.raised))
    changed = 100 * rel.removed_area / max(rel.raised.area, 1e-9)
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
            and abs(bb[2] - p.total_thickness) < 1e-3,
        ),
        (
            "Base >= 2.0 mm and base+relief <= 2.5 mm (nominal)",
            f"{p.base_thickness:.2f} + {p.relief:.2f} = {p.total_thickness:.2f} mm",
            p.base_thickness >= 2.0 and p.total_thickness <= 2.5 + 1e-9,
        ),
        (
            "Relief depth/height vs. CN-A design rule 0.8 mm (informational)",
            f"{p.relief:.2f} mm (MJF article: 0.5)",
            p.relief >= 0.8,
        ),
        (
            "Tolerance +-0.3 mm on 2.5 mm envelope (informational)",
            f"base {p.base_thickness - 0.3:.1f}..{p.base_thickness + 0.3:.1f}, "
            f"total max {p.total_thickness + 0.3:.1f} mm",
            p.total_thickness + 0.3 <= 2.5,
        ),
        (
            "Min. raised web / groove width >= 0.8 mm (opening+closing filter)",
            f"{n_raised} raised polygons, {changed:.1f} % of area adjusted by filter",
            changed < 15,
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
    ap.add_argument("--bubbles", type=int, default=None, help="through-holes (default 0)")
    ap.add_argument("--relief", type=float, default=None, help="0 = flat control variant (2.0 mm)")
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
    if a.relief is not None:
        p = replace(p, relief=a.relief)
    p.validate()
    bubbles = layout_bubbles(p)
    content = CardContent.load(a.content)
    logo = trim_logo(Image.open(a.logo))
    rel = build_front_relief(
        content.name, tuple(w for w, _ in content.badges), seed_int(p.seed), p.min_feature
    )

    a.out.mkdir(parents=True, exist_ok=True)
    part = a.part_number + ("-flat" if p.relief == 0 else "") + ("-holes" if bubbles else "")
    stem = f"NCFAI-card_{part}_EXP_MJF_PAC-HP_{a.date}"

    front = render_front(p, content, logo, bubbles, a.ppmm, rel)
    back = render_back(p, content, logo, bubbles, a.ppmm)
    mesh = build_mesh(p, bubbles, rel.raised)
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
    write_preview(a.out / f"{stem}_preview.png", p, front, back, bubbles, rel.raised, a.ppmm)
    try:
        step_ok = write_step(a.out / f"{stem}.step", p, bubbles, rel.raised)
    except Exception as exc:  # STEP is secondary; keep the print package
        print(f"STEP failed: {exc!r}")
        step_ok = False

    rows = check(p, bubbles, geo, rel)
    if content.url:
        qr = make_layout(content.url, p.width - QR_RIGHT, QR_TOP, a.ppmm)
        rows.append(
            (
                f"QR module {qr.module_mm:.2f} mm, {qr.n}x{qr.n}, ECC Q, quiet zone 4 modules",
                f"code area {qr.size:.1f} mm",
                qr.module_mm >= 1.0,
            )
        )
        vq = verify_qr(back, qr, content.url, a.ppmm)
        rows += [(f"QR decodes: {n}", "ok" if ok else "no", ok) for n, ok in vq]
        if not vq:
            print("QR decode test: skipped (zxing-cpp not installed)")
    print(
        f"seed={p.seed} tag={seed_tag(p.seed)} bubbles={len(bubbles)} bracts={len(rel.cone.tiles)}"
    )
    for name, res, ok in rows:
        info = "informational" in name
        print(f"[{'PASS' if ok else ('INFO' if info else 'FAIL')}] {name}: {res}")
    print(f"STEP: {'written' if step_ok else 'skipped/failed'}")
    print(f"files: {a.out}/{stem}*")
    return 0 if all(ok for n, _, ok in rows if "informational" not in n) else 1


if __name__ == "__main__":
    raise SystemExit(main())
