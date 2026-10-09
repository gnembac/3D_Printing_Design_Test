"""Parameters and validation for NCRAI robot card, variant A (no CAD dependency).

All lengths in millimetres, angles in degrees. Closed state = one flat 86 x 54 plate of
thickness `t` in which the robot panel lies nested in a window. A film hinge (thin web) joins
panel and plate. The part is printed in the *open* pose (web relaxed at `relax_deg`), so the
printed bounding box is larger than the closed card; closing bends the web elastically.

Rules referenced are manufacturer data (Supplier CN-A, MJF / PAC-HP, indicative values, see
docs/reference/supplier-cn-a/design-guidelines.md). The film hinge deliberately violates the
PAC-HP wall rule (2.0 mm) - it is the only way found to stay below 4 mm; see README.md.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# manufacturer data (Supplier CN-A, MJF / PAC-HP, indicative)
PAC_HP_WALL_MIN = 2.0
MJF_DETAIL_MIN = 0.8
MJF_CLEARANCE_MOVING_MIN = 0.6
# manufacturer data (print service JLC3DP, order check 2026-10-09): wall >= 1.0 mm (ideal 2.0 mm),
# embossed/engraved text and slots >= 0.8 mm for nylon/resin (>= 1.0 mm for metal/plastic)
SERVICE_WALL_MIN = 1.0
SERVICE_WALL_IDEAL = 2.0
# ASSUMPTION: elastic limit of PA12-type nylon in bending, not a PAC-HP datasheet value (k.A.)
ASSUMED_STRAIN_LIMIT = 0.05

Rect = tuple[float, float, float, float]  # (u0, u1, v0, v1) in panel coordinates, hinge at v = 0

# neutral humanoid silhouette (own design), u across (centre 0), v upwards from the hinge
SILHOUETTE: tuple[Rect, ...] = (
    (-12.0, 12.0, 0.0, 3.0),  # base bar (feet), carries the hinge web
    (-8.0, -2.0, 3.0, 12.0),  # left leg
    (2.0, 8.0, 3.0, 12.0),  # right leg
    (-8.8, 8.8, 12.0, 27.0),  # torso
    (-14.0, 14.0, 24.0, 27.0),  # shoulder bar
    (-14.0, -10.0, 12.0, 27.0),  # left arm (slit to torso 1.2 mm)
    (10.0, 14.0, 12.0, 27.0),  # right arm
    (-3.0, 3.0, 26.5, 29.5),  # neck
    (-8.0, 8.0, 29.0, 40.0),  # head
)


@dataclass(frozen=True)
class CardParams:
    card_w: float = 86.0
    card_h: float = 54.0
    t: float = 2.4  # plate and panel thickness (closed card thickness)
    gap: float = 1.0  # clearance panel <-> window (slot width, keep >= 1.0 for the print service)
    web_t: float = (
        1.1  # film hinge thickness (1.0 mm service minimum + margin for mesh tessellation)
    )
    web_len: float = 9.0  # free web length (arc length)
    web_w: float = 24.0  # web width (= base bar width)
    relax_deg: float = 45.0  # opening angle of the as-printed (relaxed) pose
    qr_cx: float = -17.0  # QR centre x on the plate (y = 0)

    @property
    def panel_w(self) -> float:
        return max(r[1] for r in SILHOUETTE) - min(r[0] for r in SILHOUETTE)

    @property
    def panel_h(self) -> float:
        return max(r[3] for r in SILHOUETTE)

    @property
    def margin(self) -> float:
        """Plate border around the window (top/bottom/right)."""
        return (self.card_h - (self.web_len + self.panel_h + self.gap)) / 2

    @property
    def window(self) -> tuple[float, float, float, float]:
        """(x0, x1, y0, y1) of the window in plate coordinates."""
        half = self.panel_w / 2 + self.gap
        x_c = self.card_w / 2 - self.margin - half
        y0 = -self.card_h / 2 + self.margin
        return x_c - half, x_c + half, y0, y0 + self.web_len + self.panel_h + self.gap

    @property
    def x_c(self) -> float:
        x0, x1, _, _ = self.window
        return (x0 + x1) / 2

    @property
    def y_e(self) -> float:
        return self.window[2]

    @property
    def relax_rad(self) -> float:
        return math.radians(self.relax_deg)

    @property
    def r_mid(self) -> float:
        """Radius of the web mid-surface in the relaxed pose."""
        return self.web_len / self.relax_rad

    @property
    def strain(self) -> float:
        """Outer-fibre strain when closing the relaxed web flat (estimated, ideal bending)."""
        return self.web_t * self.relax_rad / (2 * self.web_len)

    @property
    def closed_thickness(self) -> float:
        return self.t

    def validate(self) -> None:
        if not 0 < self.relax_deg < 120:
            raise ValueError("relax_deg must be in (0, 120)")
        if self.web_t <= 0 or self.web_len <= 0 or self.t <= self.web_t:
            raise ValueError("need 0 < web_t < t and web_len > 0")
        if self.web_w > self.panel_w:
            raise ValueError("web wider than panel")
        if self.margin < 1.5:
            raise ValueError(f"plate margin {self.margin:.2f} mm < 1.5 mm")
        if self.window[0] <= self.qr_cx + 24.6 + 1.5:
            raise ValueError("window overlaps QR area (49.2 mm code + 1.5 mm)")
        if self.qr_cx - 24.6 < -self.card_w / 2:
            raise ValueError("QR area exceeds the card")

    def mjf_findings(self) -> list[str]:
        """Deviations from Supplier CN-A MJF/PAC-HP indicative rules and risks (empty = none)."""
        out: list[str] = []
        if self.web_t < PAC_HP_WALL_MIN:
            out.append(f"web_t {self.web_t} < {PAC_HP_WALL_MIN} mm (PAC-HP wall) - film hinge")
        if self.web_t < SERVICE_WALL_MIN:
            out.append(f"web_t {self.web_t} < {SERVICE_WALL_MIN} mm (print service minimum wall)")
        if self.gap < SERVICE_WALL_MIN:
            out.append(f"gap {self.gap} < {SERVICE_WALL_MIN} mm (slot width, print service)")
        if self.gap < MJF_CLEARANCE_MOVING_MIN:
            out.append(f"gap {self.gap} < {MJF_CLEARANCE_MOVING_MIN} mm (moving parts)")
        if self.margin < PAC_HP_WALL_MIN:
            out.append(f"margin {self.margin:.2f} < {PAC_HP_WALL_MIN} mm (wall)")
        if self.strain > ASSUMED_STRAIN_LIMIT:
            out.append(f"strain {self.strain:.1%} > assumed limit {ASSUMED_STRAIN_LIMIT:.0%}")
        return out


def variant_a1() -> CardParams:
    """First submission (web 0.8 mm, gap 0.8 mm, 55 deg): flagged by the print service."""
    return CardParams(gap=0.8, web_t=0.8, relax_deg=55.0)


def variant_a2() -> CardParams:
    """Revision after the order check: web 1.1 mm, length 9 mm, gap 1.0 mm, 45 deg (default)."""
    return CardParams()
