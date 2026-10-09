"""CadQuery model of the NCRAI robot card, variant A (nested panel, film hinge).

Printed in the open pose: plate flat on z = 0 (top face z = t), web relaxed at relax_deg,
robot panel standing on the web. See ncrai_card_params.py for the concept and the rule deviations.

Usage (needs cadquery):
    python robot_card.py --out <dir> --date 2026-10-09 [--variant a1|a2]
Writes NCRAI-card_variant-A[2]_EXP_MJF_PAC-HP_<date>.step (geometry only) and a scratch STL
(<name>.stl, input for card_colour.py).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ncrai_card_params import (  # noqa: E402
    SILHOUETTE,
    CardParams,
    variant_a1,
    variant_a2,
)

NAMES = {"a1": "NCRAI-card_variant-A_EXP_MJF_PAC-HP", "a2": "NCRAI-card_variant-A2_EXP_MJF_PAC-HP"}
PRESETS = {"a1": variant_a1, "a2": variant_a2}


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").add(
        cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
    )


def panel_flat(p: CardParams) -> cq.Workplane:
    """Panel in local coordinates (u across, v up, z' thickness, web mid-plane at z' = 0)."""
    z0, z1 = -p.web_t / 2, p.t - p.web_t / 2
    solid: cq.Workplane | None = None
    for u0, u1, v0, v1 in SILHOUETTE:
        if v0 == 0.0:
            v0 = -0.2  # overlap with the web end for a clean union
        part = _box(u0, u1, v0, v1, z0, z1)
        solid = part if solid is None else solid.union(part)
    assert solid is not None
    return solid


def web(p: CardParams) -> cq.Workplane:
    """Straight anchor strip inside the plate plus the relaxed arc up to the panel."""
    ro, ri = p.r_mid + p.web_t / 2, p.r_mid - p.web_t / 2
    zc = ro  # outer surface at z = 0
    a = p.relax_rad

    def pt(r: float, phi: float) -> tuple[float, float]:
        return r * math.sin(phi), zc - r * math.cos(phi)  # (dy, z) relative to y_e

    y0 = p.y_e
    sector = (
        cq.Workplane("YZ")
        .moveTo(y0 + pt(ro, 0)[0], pt(ro, 0)[1])
        .threePointArc((y0 + pt(ro, a / 2)[0], pt(ro, a / 2)[1]), (y0 + pt(ro, a)[0], pt(ro, a)[1]))
        .lineTo(y0 + pt(ri, a)[0], pt(ri, a)[1])
        .threePointArc((y0 + pt(ri, a / 2)[0], pt(ri, a / 2)[1]), (y0 + pt(ri, 0)[0], pt(ri, 0)[1]))
        .close()
        .extrude(p.web_w)
        .translate((p.x_c - p.web_w / 2, 0, 0))
    )
    anchor = _box(p.x_c - p.web_w / 2, p.x_c + p.web_w / 2, p.y_e - 1.0, p.y_e, 0, p.web_t)
    return sector.union(anchor)


def panel_pose(p: CardParams) -> tuple[float, float]:
    """(y, z) of the web end (mid-thickness) in the relaxed pose."""
    a = p.relax_rad
    zc = p.r_mid + p.web_t / 2
    return p.y_e + p.r_mid * math.sin(a), zc - p.r_mid * math.cos(a)


def build(p: CardParams | None = None) -> cq.Workplane:
    p = p or CardParams()
    p.validate()
    x0, x1, y0, y1 = p.window
    plate = _box(-p.card_w / 2, p.card_w / 2, -p.card_h / 2, p.card_h / 2, 0, p.t)
    plate = plate.cut(_box(x0, x1, y0, y1, -1, p.t + 1))
    ey, ez = panel_pose(p)
    panel = panel_flat(p).rotate((0, 0, 0), (1, 0, 0), p.relax_deg).translate((p.x_c, ey, ez))
    return plate.union(web(p)).union(panel)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--variant", choices=sorted(PRESETS), default="a2")
    ns = ap.parse_args()
    ns.out.mkdir(parents=True, exist_ok=True)
    model = build(PRESETS[ns.variant]())
    stem = f"{NAMES[ns.variant]}_{ns.date}"
    cq.exporters.export(model, str(ns.out / f"{stem}.step"))
    cq.exporters.export(model, str(ns.out / f"{stem}.stl"), tolerance=0.01, angularTolerance=0.05)
    print(f"wrote {stem}.step/.stl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
