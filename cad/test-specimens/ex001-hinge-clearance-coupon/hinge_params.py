"""Parameters and validation for EX-001 (print-in-place pin hinge, clearance series).

No CAD dependency. All lengths in millimetres.

Hinge layout (axis along Y): leaf A carries the outer knuckles and the pin, leaf B carries the
middle knuckle with the bore. Radial gap = axial gap = clearance. Rules checked here are
manufacturer data (Supplier CN-A, MJF, indicative values, see
docs/reference/supplier-cn-a/design-guidelines.md); they apply to the later MJF card, the
coupon itself is meant to be printed on the own FDM printer first.
"""

from __future__ import annotations

from dataclasses import dataclass

# manufacturer data (Supplier CN-A, MJF, indicative): minimum gap for moving / print-in-place parts
MJF_CLEARANCE_MOVING_MIN = 0.6
# manufacturer data (Supplier CN-A, MJF): minimum pin diameter, wall for bosses/snap fits
MJF_PIN_DIA_MIN = 2.0
MJF_FEATURE_WALL_MIN = 1.5
# manufacturer data (Supplier CN-A, MJF, PAC-HP): minimum wall thickness
PAC_HP_WALL_MIN = 2.0

DEFAULT_CLEARANCES: tuple[float, ...] = (0.30, 0.40, 0.50, 0.60, 0.80, 1.00)


@dataclass(frozen=True)
class HingeParams:
    clearance: float = 0.6
    pin_d: float = 2.5
    knuckle_wall: float = 2.5  # radial wall around the bore
    leaf_w: float = 14.0  # leaf length perpendicular to the axis
    leaf_t: float = 2.5  # leaf thickness
    axis_len: float = 30.0  # total hinge length along the axis

    @property
    def bore_d(self) -> float:
        return self.pin_d + 2 * self.clearance

    @property
    def knuckle_d(self) -> float:
        return self.bore_d + 2 * self.knuckle_wall

    @property
    def knuckle_len(self) -> float:
        """Length of each of the three knuckles (two axial gaps of `clearance`)."""
        return (self.axis_len - 2 * self.clearance) / 3

    def validate(self) -> None:
        if self.clearance <= 0:
            raise ValueError("clearance must be > 0")
        if self.pin_d <= 0 or self.knuckle_wall <= 0 or self.leaf_w <= 0:
            raise ValueError("pin_d, knuckle_wall and leaf_w must be > 0")
        if self.knuckle_len < 4.0:
            raise ValueError(f"knuckle_len {self.knuckle_len:.2f} mm < 4 mm")
        if self.leaf_t > self.knuckle_d:
            raise ValueError("leaf thicker than knuckle diameter")
        if self.leaf_w <= self.knuckle_d / 2:
            raise ValueError("leaf_w must exceed the knuckle radius")

    def mjf_findings(self) -> list[str]:
        """Deviations from the Supplier CN-A MJF/PAC-HP indicative rules (empty = none)."""
        out: list[str] = []
        if self.clearance < MJF_CLEARANCE_MOVING_MIN:
            out.append(f"clearance {self.clearance} < {MJF_CLEARANCE_MOVING_MIN} mm (moving parts)")
        if self.pin_d < MJF_PIN_DIA_MIN:
            out.append(f"pin_d {self.pin_d} < {MJF_PIN_DIA_MIN} mm")
        if self.knuckle_wall < PAC_HP_WALL_MIN:
            out.append(f"knuckle_wall {self.knuckle_wall} < {PAC_HP_WALL_MIN} mm (PAC-HP wall)")
        if self.leaf_t < PAC_HP_WALL_MIN:
            out.append(f"leaf_t {self.leaf_t} < {PAC_HP_WALL_MIN} mm (PAC-HP wall)")
        return out


def series(clearances: tuple[float, ...] = DEFAULT_CLEARANCES) -> list[HingeParams]:
    """One validated HingeParams per clearance value."""
    result = [HingeParams(clearance=c) for c in clearances]
    for p in result:
        p.validate()
    return result
