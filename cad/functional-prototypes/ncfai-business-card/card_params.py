"""Parameters, validation and seeded "bubble" layout for the NCFAI 3D-printed business card.

All lengths in mm. Card coordinates for the layout: origin top-left of the front face,
x to the right, y downwards (as in an image). Mesh coordinates are centred (see ncfai_card.py).

Supplier values (wall >= 2.0 mm, tolerance +/-0.3 mm, hole >= 1.5 mm) are manufacturer data of
Supplier CN-A (PAC-HP full-colour MJF nylon), indicative only; see
docs/reference/supplier-cn-a/design-guidelines.md.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field

# --- manufacturer data (Supplier CN-A, PAC-HP, indicative values) --------------------------
SUPPLIER_WALL_MIN = 2.0  # PAC-HP minimum wall thickness
SUPPLIER_TOL = 0.3  # +/- general tolerance, models <= 100 mm
SUPPLIER_HOLE_MIN = 1.5  # minimum hole diameter (holes tend to come out undersize)
# --- project requirement -----------------------------------------------------------------
THICKNESS_MAX = 2.5  # user requirement: material thickness max. 2.5 mm


@dataclass(frozen=True)
class Bubble:
    x: float  # card coordinates, mm
    y: float
    d: float  # hole diameter, mm


@dataclass(frozen=True)
class CardParams:
    width: float = 85.0
    height: float = 55.0
    thickness: float = 2.2  # nominal; 2.2 + 0.3 tol = 2.5 max, 2.2 > wall min 2.0
    corner_r: float = 4.0  # outer corner radius (no sharp corners -> less warp-prone)
    seed: str = "NCFAI-UNIKAT-001"
    n_bubbles: int = 7  # 0 = flat control variant without perforation
    bubble_d_min: float = 2.6
    bubble_d_max: float = 4.6
    ligament_min: float = 2.4  # min. material between holes (supplier wall min 2.0 + margin)
    edge_margin: float = 4.0  # min. distance hole edge -> card edge
    # zone (x0, y0, x1, y1) in card coordinates in which bubble holes may lie
    bubble_zone: tuple[float, float, float, float] = field(default=(49.0, 35.0, 81.0, 51.0))
    arc_tol: float = 0.02  # max. chord error when discretising circles, mm

    def validate(self) -> None:
        if self.thickness < SUPPLIER_WALL_MIN:
            raise ValueError(f"thickness {self.thickness} < supplier wall minimum")
        if self.thickness + SUPPLIER_TOL > THICKNESS_MAX + 1e-9:
            raise ValueError(
                f"thickness {self.thickness} + tolerance {SUPPLIER_TOL} exceeds {THICKNESS_MAX} mm"
            )
        if not 2.0 <= self.corner_r <= min(self.width, self.height) / 2:
            raise ValueError("corner_r must be 2 mm .. half of the short side")
        if self.n_bubbles < 0:
            raise ValueError("n_bubbles must be >= 0")
        if self.bubble_d_min < max(SUPPLIER_HOLE_MIN + 2 * SUPPLIER_TOL, 2.4):
            raise ValueError("bubble_d_min too small (holes tend to come out undersize)")
        if self.bubble_d_max < self.bubble_d_min:
            raise ValueError("bubble_d_max < bubble_d_min")
        if self.ligament_min < SUPPLIER_WALL_MIN:
            raise ValueError("ligament_min below supplier wall minimum")
        if self.edge_margin < SUPPLIER_WALL_MIN:
            raise ValueError("edge_margin below supplier wall minimum")
        x0, y0, x1, y1 = self.bubble_zone
        if not (0 <= x0 < x1 <= self.width and 0 <= y0 < y1 <= self.height):
            raise ValueError("bubble_zone outside card")


def seed_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16], 16)


def seed_tag(seed: str) -> str:
    """Short fingerprint printed on the back (identifies this unique card)."""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8].upper()


def _circle_clear(a: Bubble, b: Bubble, gap: float) -> bool:
    return math.hypot(a.x - b.x, a.y - b.y) - (a.d + b.d) / 2 >= gap


def layout_bubbles(p: CardParams) -> list[Bubble]:
    """Seeded, reproducible hole layout. Same seed + params -> identical card (the Unikat)."""
    p.validate()
    if p.n_bubbles == 0:
        return []
    rng = random.Random(seed_int(p.seed))
    x0, y0, x1, y1 = p.bubble_zone
    # largest first: packs reliably; sizes are spread over the allowed range
    diams = sorted(
        (round(rng.uniform(p.bubble_d_min, p.bubble_d_max), 1) for _ in range(p.n_bubbles)),
        reverse=True,
    )
    placed: list[Bubble] = []
    for d in diams:
        r = d / 2
        lo_x = max(x0 + r, p.edge_margin + r)
        hi_x = min(x1 - r, p.width - p.edge_margin - r)
        lo_y = max(y0 + r, p.edge_margin + r)
        hi_y = min(y1 - r, p.height - p.edge_margin - r)
        for _ in range(20000):
            cand = Bubble(round(rng.uniform(lo_x, hi_x), 2), round(rng.uniform(lo_y, hi_y), 2), d)
            if all(_circle_clear(cand, o, p.ligament_min) for o in placed):
                placed.append(cand)
                break
        else:
            raise ValueError(f"cannot place bubble d={d}: zone too small for n={p.n_bubbles}")
    return placed


def min_ligament(p: CardParams, bubbles: list[Bubble]) -> float:
    """Smallest material web: hole-hole and hole-card-edge (straight edges; corners are farther)."""
    webs = [math.inf]
    for i, a in enumerate(bubbles):
        for b in bubbles[i + 1 :]:
            webs.append(math.hypot(a.x - b.x, a.y - b.y) - (a.d + b.d) / 2)
        r = a.d / 2
        webs += [a.x - r, p.width - a.x - r, a.y - r, p.height - a.y - r]
    return min(webs)
