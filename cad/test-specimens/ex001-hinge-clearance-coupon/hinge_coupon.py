"""EX-001 coupon: six print-in-place pin hinges with different clearances (CadQuery).

Axis along Y, leaves flat on the build plate (z = 0), pin integral with leaf A.
Hinge n carries n dots on leaf A (ID 1..6, clearance order see hinge_params.DEFAULT_CLEARANCES).

Usage (needs cadquery):
    python hinge_coupon.py --out <dir> --date 2026-10-09 [--process FDM --material PLA]
Writes EX001_hinge-clearance-coupon_EXP_<process>_<material>_<date>.step / .stl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hinge_params import HingeParams, series  # noqa: E402

GAP_BETWEEN = 8.0  # spacing between hinges on the plate
DOT_D, DOT_H, DOT_PITCH = 1.6, 0.8, 2.6


def _cyl(r: float, y0: float, y1: float, zc: float) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(0, y0, zc), cq.Vector(0, 1, 0))
    return cq.Workplane("XY").add(solid)


def _box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").add(
        cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))
    )


def build_hinge(p: HingeParams, n_dots: int) -> tuple[cq.Workplane, cq.Workplane]:
    """Return (leaf A incl. pin, leaf B) as separate solids."""
    p.validate()
    r, zc = p.knuckle_d / 2, p.knuckle_d / 2
    c, kl = p.clearance, p.knuckle_len
    a1 = (0.0, kl)
    b = (kl + c, 2 * kl + c)
    a3 = (2 * kl + 2 * c, p.axis_len)

    leaf_a = _box(-p.leaf_w, 0, 0, p.axis_len, 0, p.leaf_t)
    leaf_a = leaf_a.cut(_cyl(r + c, b[0] - c, b[1] + c, zc))  # clear the middle knuckle
    for y0, y1 in (a1, a3):
        leaf_a = leaf_a.union(_cyl(r, y0, y1, zc))
    leaf_a = leaf_a.union(_cyl(p.pin_d / 2, 0, p.axis_len, zc))
    for i in range(n_dots):
        x = -p.leaf_w + 3.0 + i * DOT_PITCH
        dot = cq.Workplane("XY").add(
            cq.Solid.makeCylinder(DOT_D / 2, DOT_H, cq.Vector(x, p.axis_len - 3.0, p.leaf_t))
        )
        leaf_a = leaf_a.union(dot)

    leaf_b = _box(0, p.leaf_w, b[0], b[1], 0, p.leaf_t)
    leaf_b = leaf_b.union(_cyl(r, b[0], b[1], zc))
    leaf_b = leaf_b.cut(_cyl(p.bore_d / 2, b[0] - 1, b[1] + 1, zc))
    return leaf_a, leaf_b


def build_coupon() -> cq.Workplane:
    """All hinges on one plate: 3 columns x 2 rows, ordered by clearance."""
    params = series()
    pitch_x = 2 * params[0].leaf_w + GAP_BETWEEN
    pitch_y = params[0].axis_len + GAP_BETWEEN
    result: cq.Workplane | None = None
    for i, p in enumerate(params):
        col, row = i % 3, i // 3
        offset = cq.Vector(col * pitch_x + p.leaf_w, row * pitch_y, 0)
        for part in build_hinge(p, i + 1):
            moved = part.translate(offset)
            result = moved if result is None else result.add(moved)
    assert result is not None
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--process", default="FDM")
    ap.add_argument("--material", default="PLA")
    ns = ap.parse_args()
    compound = cq.Compound.makeCompound([o for o in build_coupon().vals()])
    stem = f"EX001_hinge-clearance-coupon_EXP_{ns.process}_{ns.material}_{ns.date}"
    ns.out.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(cq.Workplane(obj=compound), str(ns.out / f"{stem}.step"))
    cq.exporters.export(cq.Workplane(obj=compound), str(ns.out / f"{stem}.stl"))
    print(f"wrote {stem}.step/.stl, {len(compound.Solids())} solids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
