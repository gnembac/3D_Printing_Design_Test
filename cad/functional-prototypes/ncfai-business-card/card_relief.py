"""Vector relief design of the card front (raised name) and icon shapes (robot head, chip).

Everything is built as shapely geometry in CARD coordinates (mm, origin top-left, y down).
Two height levels only: base plane (z = base_thickness) and raised plane (+relief).
"Engraved" means: a groove/letter cut *into a raised area* down to the base plane, so the
wall under it never gets thinner than the base (supplier wall minimum, see card_params.py).

The same geometry drives the 3D mesh and the colour texture -> perfect registration.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

# Relief lettering uses DejaVu Sans Bold: heavier, more uniform strokes (stem ~0.18 em,
# horizontals ~0.15 em) than Liberation Sans Bold -> survives the 0.7 mm minimum-feature filter.
FONT_FILES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
)


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
    """Height of capital 'H' (font-independent: measured from the glyph outline)."""
    f = _font(font_path())
    pen = _FlatPen(f.getGlyphSet())
    f.getGlyphSet()[f.getBestCmap()[ord("H")]].draw(pen)
    top = max(y for ring in pen.rings for _, y in ring)
    return top * size_mm / f["head"].unitsPerEm


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


def enforce_min_feature(geom: BaseGeometry, w: float) -> BaseGeometry:
    """Opening then closing with radius ~w/2: no raised web and no groove narrower than w."""
    r = w / 2 - 0.01
    g = geom.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)
    return g.buffer(r, quad_segs=8).buffer(-r, quad_segs=8)


NAME_X, NAME_BASE = 5.0, 40.6
GIVEN_SIZE, FAMILY_SIZE = 6.8, 5.6  # given name one size larger than the family name
LIST_X, LIST_SIZE = 5.0, 4.7  # dash list: raised DOEMENS line, engraved BJCP line
DOEMENS_BASE, BJCP_BASE = 27.6, 33.0
LIST_MAX_RIGHT = 81.5  # raised text keeps >= 3 mm from the card edge (85 - 3.5)


@dataclass(frozen=True)
class FrontRelief:
    name: BaseGeometry  # raised
    doemens: BaseGeometry  # raised
    recess: BaseGeometry  # BJCP lettering, cut below the base plane
    raised: BaseGeometry  # name + doemens after minimum-feature enforcement
    removed_area: float  # mm2 changed by enforce_min_feature (should be small)


def build_front_relief(
    name: str,
    min_feature: float,
    doemens: str = "DOEMENS BIERSOMMELIER",
    bjcp: str = "BJCP BEER JUDGE",
) -> FrontRelief:
    first, _, last = name.partition(" ")
    x_last = NAME_X + text_width(first, GIVEN_SIZE) + text_width(" ", FAMILY_SIZE)
    name_geom = unary_union(
        [
            text_geometry(first, GIVEN_SIZE, NAME_X, NAME_BASE),
            text_geometry(last, FAMILY_SIZE, x_last, NAME_BASE),
        ]
    )
    lines = []
    for text, base in (("\u2013 " + doemens, DOEMENS_BASE), ("\u2013 " + bjcp, BJCP_BASE)):
        right = LIST_X + text_width(text, LIST_SIZE)
        if right > LIST_MAX_RIGHT:
            raise ValueError(f"'{text}' too wide ({right:.1f} mm > {LIST_MAX_RIGHT} mm)")
        lines.append(text_geometry(text, LIST_SIZE, LIST_X, base))
    recess = enforce_min_feature(lines[1], min_feature)
    raw = unary_union([name_geom, lines[0]])
    raised = enforce_min_feature(raw, min_feature)
    return FrontRelief(name_geom, lines[0], recess, raised, raw.symmetric_difference(raised).area)
