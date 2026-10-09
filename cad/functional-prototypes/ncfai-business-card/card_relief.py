"""Vector relief design of the card front: raised name, badges with engraved lettering, hop cone.

Everything is built as shapely geometry in CARD coordinates (mm, origin top-left, y down).
Two height levels only: base plane (z = base_thickness) and raised plane (+relief).
"Engraved" means: a groove/letter cut *into a raised area* down to the base plane, so the
wall under it never gets thinner than the base (supplier wall minimum, see card_params.py).

The same geometry drives the 3D mesh and the colour texture -> perfect registration.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

FONT_FILES = (
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)

# Hop cone placement (card coordinates, mm)
CONE_CX, CONE_TOP, CONE_TIP, CONE_W = 71.2, 29.6, 51.6, 16.4
ICON_CX = 77.0  # robot head / chip icon column (top right)
GROOVE = 0.85  # groove between bracts (>= 0.8 mm supplier minimum, conservative value)


def parts(geom: BaseGeometry) -> list[Polygon]:
    """All polygons of a (multi)geometry, empty ones dropped."""
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [q for g in getattr(geom, "geoms", []) for q in parts(g)]


def font_path() -> str:
    for f in FONT_FILES:
        if Path(f).exists():
            return f
    raise FileNotFoundError("no bold sans font found (Liberation Sans / DejaVu Sans)")


class _FlatPen(BasePen):
    """Collects glyph outlines as polylines (curves flattened)."""

    def __init__(self, glyph_set: object, steps: int = 10) -> None:
        super().__init__(glyph_set)
        self.rings: list[list[tuple[float, float]]] = []
        self._cur: list[tuple[float, float]] = []
        self._steps = steps

    def _moveTo(self, pt: tuple[float, float]) -> None:
        self._cur = [pt]

    def _lineTo(self, pt: tuple[float, float]) -> None:
        self._cur.append(pt)

    def _curveToOne(self, p1, p2, p3) -> None:  # noqa: ANN001
        p0 = self._cur[-1]
        for i in range(1, self._steps + 1):
            t = i / self._steps
            a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t**2 * (1 - t), t**3
            self._cur.append(
                (
                    a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
                )
            )

    def _qCurveToOne(self, p1, p2) -> None:  # noqa: ANN001
        p0 = self._cur[-1]
        for i in range(1, self._steps + 1):
            t = i / self._steps
            a, b, c = (1 - t) ** 2, 2 * t * (1 - t), t**2
            self._cur.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))

    def _closePath(self) -> None:
        if len(self._cur) >= 3:
            self.rings.append(self._cur)
        self._cur = []

    _endPath = _closePath


@lru_cache(maxsize=4)
def _font(path: str) -> TTFont:
    return TTFont(path)


def text_width(text: str, size_mm: float, tracking: float = 0.0) -> float:
    """Advance width in mm; `tracking` = extra letter spacing in mm (between letters only)."""
    f = _font(font_path())
    scale = size_mm / f["head"].unitsPerEm
    cmap = f.getBestCmap()
    return sum(f["hmtx"][cmap[ord(c)]][0] for c in text) * scale + tracking * (len(text) - 1)


def cap_height(size_mm: float) -> float:
    f = _font(font_path())
    return f["OS/2"].sCapHeight * size_mm / f["head"].unitsPerEm


def text_geometry(
    text: str, size_mm: float, x: float, baseline: float, anchor: str = "l", tracking: float = 0.0
) -> BaseGeometry:
    """Glyph outlines as shapely geometry (card coordinates, y down). anchor: l | c."""
    f = _font(font_path())
    scale = size_mm / f["head"].unitsPerEm
    cmap, glyphs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    x0 = x - (text_width(text, size_mm, tracking) / 2 if anchor == "c" else 0.0)
    out: list[BaseGeometry] = []
    cursor = 0.0
    for ch in text:
        name = cmap[ord(ch)]
        pen = _FlatPen(glyphs)
        glyphs[name].draw(pen)
        g: BaseGeometry = Polygon()
        for ring in pen.rings:  # TrueType: holes are opposite-wound rings -> XOR
            g = g.symmetric_difference(Polygon(ring).buffer(0))
        if not g.is_empty:
            out.append(
                affinity.affine_transform(g, [scale, 0, 0, -scale, x0 + cursor * scale, baseline])
            )
        cursor += hmtx[name][0] + tracking / scale
    return unary_union(out)


BADGE_SIZE, BADGE_PAD, BADGE_H, BADGE_Y, BADGE_GAP, BADGE_TRACK = 5.2, 2.3, 8.2, 31.0, 2.4, 0.35


def badge(word: str, x0: float, shape: str) -> tuple[BaseGeometry, float]:
    """Raised badge with the word ENGRAVED into it (down to the base plane).

    shape: "capsule" (institution) or "chamfer" (judge seal, bevelled corners). Returns (geom, w).
    """
    h, y0 = BADGE_H, BADGE_Y
    w = text_width(word, BADGE_SIZE, BADGE_TRACK) + 2 * BADGE_PAD
    if shape == "capsule":
        r = h / 2
        body: BaseGeometry = box(x0 + r, y0 + r, x0 + w - r, y0 + h - r).buffer(r, quad_segs=24)
    else:
        c = 2.2
        body = box(x0 + c, y0 + c, x0 + w - c, y0 + h - c).buffer(c, join_style=3, mitre_limit=1.0)
    base_y = y0 + h / 2 + cap_height(BADGE_SIZE) / 2
    letters = text_geometry(word, BADGE_SIZE, x0 + w / 2, base_y, anchor="c", tracking=BADGE_TRACK)
    return body.difference(letters), w


def robot_head(cx: float, top: float) -> BaseGeometry:
    """Robotics icon: head with antenna, ears and engraved eyes/mouth (all features >= 0.85 mm)."""
    head = box(cx - 3.0, top + 2.1, cx + 3.0, top + 7.9)
    head = head.buffer(-0.7).buffer(0.7, quad_segs=8)  # rounded corners
    ears = unary_union(
        [
            box(cx - 3.9, top + 3.6, cx - 3.0, top + 6.4),
            box(cx + 3.0, top + 3.6, cx + 3.9, top + 6.4),
        ]
    )
    antenna = unary_union(
        [box(cx - 0.45, top + 1.0, cx + 0.45, top + 2.2), Point(cx, top + 1.0).buffer(0.95)]
    )
    eyes = unary_union(
        [Point(cx - 1.55, top + 4.3).buffer(0.9), Point(cx + 1.55, top + 4.3).buffer(0.9)]
    )
    mouth = box(cx - 1.9, top + 6.0, cx + 1.9, top + 6.9)
    return unary_union([head, ears, antenna]).difference(unary_union([eyes, mouth]))


def chip_icon(cx: float, top: float) -> BaseGeometry:
    """AI icon: microchip (3 pins per side, engraved square die ring around a raised core)."""
    body = box(cx - 2.6, top + 1.1, cx + 2.6, top + 6.3)
    mid = top + 3.7
    pins = []
    for k in (-1.7, 0.0, 1.7):  # 0.85 wide, gap 0.85
        pins += [
            box(cx + k - 0.425, top, cx + k + 0.425, top + 1.1),
            box(cx + k - 0.425, top + 6.3, cx + k + 0.425, top + 7.4),
            box(cx - 3.7, mid + k - 0.425, cx - 2.6, mid + k + 0.425),
            box(cx + 2.6, mid + k - 0.425, cx + 3.7, mid + k + 0.425),
        ]
    ring = box(cx - 1.75, mid - 1.75, cx + 1.75, mid + 1.75).difference(
        box(cx - 0.85, mid - 0.85, cx + 0.85, mid + 0.85)
    )
    return unary_union([body, *pins]).difference(ring)


@dataclass(frozen=True)
class HopCone:
    silhouette: Polygon  # base-level floor (printed dark green)
    tiles: tuple[tuple[Polygon, float], ...]  # raised bracts with colour parameter t 0 (top)..1
    stalk: Polygon


def _half_width(s: float) -> float:
    return (CONE_W / 2) * max(0.0, math.sin(math.pi * s**0.7)) ** 0.8


def hop_cone(seed: int, gap: float = GROOVE, min_feature: float = 0.8) -> HopCone:
    """Female hop cone, tip down: overlapping bracts as raised tiles separated by grooves.

    Seed jitter (bract position/size/splay, bend, stalk) makes every card's cone unique.
    """
    rng = random.Random(seed ^ 0x9E3779B9)
    bend = rng.uniform(-0.9, 0.9)
    h = CONE_TIP - CONE_TOP

    def cx_at(s: float) -> float:
        return CONE_CX + bend * math.sin(math.pi * s)

    pts_l, pts_r = [], []
    for i in range(121):
        s = i / 120
        y, w, c = CONE_TOP + s * h, _half_width(s), cx_at(s)
        pts_l.append((c - w, y))
        pts_r.append((c + w, y))
    sil = Polygon(pts_l + pts_r[::-1]).buffer(0)

    tiles: list[tuple[Polygon, float]] = []
    placed: list[BaseGeometry] = []
    dy = 3.0
    k = 0
    y = CONE_TOP + 1.5
    while y < CONE_TIP - 1.0:
        s = (y - CONE_TOP) / h
        w = _half_width(s)
        n = max(1, round(2 * w / 4.9))
        pitch = 2 * w / n
        shift = (0.25 if k % 2 else -0.25) * pitch if n > 1 else 0.0
        for i in range(n):
            x = cx_at(s) + (i - (n - 1) / 2) * pitch + shift + rng.uniform(-0.25, 0.25)
            yy = y + rng.uniform(-0.2, 0.2)
            rx = pitch * rng.uniform(0.58, 0.66)
            ry = dy * rng.uniform(0.85, 0.98)
            ell = affinity.scale(Point(0, 0).buffer(1.0, quad_segs=24), rx, ry)
            ell = affinity.rotate(ell, (x - cx_at(s)) / max(w, 1.0) * 14 + rng.uniform(-4, 4))
            tile = affinity.translate(ell, x, yy).intersection(sil)
            if placed:
                tile = tile.difference(unary_union(placed).buffer(gap, quad_segs=8))
            tile = max(parts(tile), key=lambda q: q.area, default=Polygon())
            if tile.is_empty:
                continue
            r = min_feature / 2 - 0.01  # opening: removes slivers narrower than min_feature
            tile = tile.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
            if tile.is_empty or tile.area < 1.2:
                continue
            tile = max(parts(tile), key=lambda q: q.area)
            tiles.append((tile, min(1.0, max(0.0, s + rng.uniform(-0.06, 0.06)))))
            placed.append(tile)
        y += dy
        k += 1
    sx = CONE_CX + rng.uniform(0.8, 2.2)
    stalk = LineString(
        [(CONE_CX, CONE_TOP + 0.8), (CONE_CX + 0.2, CONE_TOP - 1.8), (sx, CONE_TOP - 3.2)]
    ).buffer(0.75, quad_segs=8)
    return HopCone(sil, tuple(tiles), stalk)


def enforce_min_feature(geom: BaseGeometry, w: float) -> BaseGeometry:
    """Opening then closing with radius ~w/2: no raised web and no groove narrower than w."""
    r = w / 2 - 0.01
    g = geom.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
    return g.buffer(r, quad_segs=8).buffer(-r, quad_segs=8)


@dataclass(frozen=True)
class FrontRelief:
    name: BaseGeometry
    badges: BaseGeometry  # union of all badges
    badge_list: tuple[BaseGeometry, ...]
    robot: BaseGeometry
    chip: BaseGeometry
    cone: HopCone
    raised: BaseGeometry  # union, after minimum-feature enforcement
    removed_area: float  # mm2 changed by enforce_min_feature (should be small)


BADGE_SHAPES = ("capsule", "chamfer")


def badge_layout(badge_words: tuple[str, ...]) -> list[tuple[float, float]]:
    """(x0, width) of every badge, left-aligned from x = 5 mm."""
    out, x = [], 5.0
    for word in badge_words:
        w = text_width(word, BADGE_SIZE, BADGE_TRACK) + 2 * BADGE_PAD
        out.append((x, w))
        x += w + BADGE_GAP
    return out


def build_front_relief(
    name: str,
    badge_words: tuple[str, ...],
    seed: int,
    min_feature: float,
) -> FrontRelief:
    first, _, last = name.partition(" ")
    name_geom = unary_union(
        [
            text_geometry(first, 6.8, 41.0, 10.9),
            text_geometry(last, 6.8, 41.0, 19.0),
        ]
    )
    badge_list = tuple(
        badge(word, x, BADGE_SHAPES[i % len(BADGE_SHAPES)])[0]
        for i, (word, (x, _)) in enumerate(zip(badge_words, badge_layout(badge_words), strict=True))
    )
    badges = unary_union(badge_list) if badge_list else Polygon()
    robot = robot_head(ICON_CX, 4.6)
    chip = chip_icon(ICON_CX, 13.6)
    cone = hop_cone(seed, min_feature=min_feature)
    raw = unary_union([name_geom, badges, robot, chip, cone.stalk, *[t for t, _ in cone.tiles]])
    raised = enforce_min_feature(raw, min_feature)
    return FrontRelief(
        name_geom,
        badges,
        badge_list,
        robot,
        chip,
        cone,
        raised,
        raw.symmetric_difference(raised).area,
    )
