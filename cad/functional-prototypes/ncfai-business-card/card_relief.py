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


NAME_SIZE, NAME_X, NAME_BASE = 5.4, 5.0, 41.0  # raised, above the address block
DOEMENS_BASE, DOEMENS_MAX_W = 31.2, 78.8  # raised, centred on the card
PANEL_RIGHT, PANEL_Y0, PANEL_Y1 = 81.0, 33.4, 51.4  # flat blue panel (BJCP), letters recessed
BJCP_SIZE, BJCP_PAD, BJCP_GAP = 5.4, 1.8, 1.6


@dataclass(frozen=True)
class FrontRelief:
    name: BaseGeometry  # raised
    doemens: BaseGeometry  # raised
    panel: BaseGeometry  # flat colour panel on the base plane (no height)
    recess: BaseGeometry  # letters cut below the base plane inside the panel
    raised: BaseGeometry  # name + doemens after minimum-feature enforcement
    removed_area: float  # mm2 changed by enforce_min_feature (should be small)


def build_front_relief(
    name: str,
    min_feature: float,
    doemens: str = "DOEMENS BIERSOMMELIER",
    bjcp: tuple[str, ...] = ("BJCP", "Beer", "Judge"),
    card_width: float = 85.0,
) -> FrontRelief:
    name_geom = text_geometry(name, NAME_SIZE, NAME_X, NAME_BASE)
    size = min(5.8, DOEMENS_MAX_W / text_width(doemens, 1.0))
    if size < 4.9:  # DejaVu Bold horizontals ~0.15 em must stay >= ~0.7 mm
        raise ValueError(f"'{doemens}' too long for one raised line (size {size:.2f} < 4.9 mm)")
    doem = text_geometry(doemens, size, card_width / 2, DOEMENS_BASE, anchor="c")
    # BJCP panel: stacked engraved lines, centred in a rounded blue panel at the bottom right
    w = max(text_width(line, BJCP_SIZE) for line in bjcp) + 2 * BJCP_PAD
    x0 = PANEL_RIGHT - w
    r = 2.0
    panel = box(x0 + r, PANEL_Y0 + r, PANEL_RIGHT - r, PANEL_Y1 - r).buffer(r, quad_segs=16)
    cap = cap_height(BJCP_SIZE)
    top = (PANEL_Y0 + PANEL_Y1) / 2 - (len(bjcp) * cap + (len(bjcp) - 1) * BJCP_GAP) / 2
    letters = unary_union(
        [
            text_geometry(line, BJCP_SIZE, x0 + w / 2, top + cap + i * (cap + BJCP_GAP), "c")
            for i, line in enumerate(bjcp)
        ]
    )
    recess = enforce_min_feature(letters, min_feature)
    raw = unary_union([name_geom, doem])
    raised = enforce_min_feature(raw, min_feature)
    return FrontRelief(
        name_geom, doem, panel, recess, raised, raw.symmetric_difference(raised).area
    )
