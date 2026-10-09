"""QR code layout for the card back, optimised for inkjet colour print on porous MJF nylon.

Print rules applied (`ASSUMPTION`, to be confirmed with a first article):
- error correction Q (25 %): tolerates dot gain, powder grain and small surface defects
- module >= 1.2 mm, snapped to an integer number of texture pixels (no anti-aliased edges)
- quiet zone 4 modules (ISO/IEC 18004), kept free of any ink
- near-black modules on bare white: maximum contrast, no gradient inside the code
"""

from __future__ import annotations

from dataclasses import dataclass

QUIET_MODULES = 4
MODULE_MM = 1.2


@dataclass(frozen=True)
class QrLayout:
    matrix: tuple[tuple[bool, ...], ...]  # True = dark module
    module_mm: float
    x: float  # top-left of the module area (not the quiet zone), image coordinates, mm
    y: float

    @property
    def n(self) -> int:
        return len(self.matrix)

    @property
    def size(self) -> float:
        return self.n * self.module_mm

    @property
    def keep_out(self) -> tuple[float, float, float, float]:
        """Module area plus quiet zone: (x0, y0, x1, y1) in mm."""
        q = QUIET_MODULES * self.module_mm
        return (self.x - q, self.y - q, self.x + self.size + q, self.y + self.size + q)


def qr_matrix(url: str, error: str = "q") -> tuple[tuple[bool, ...], ...]:
    import segno

    code = segno.make(url, error=error, micro=False, boost_error=False)
    return tuple(tuple(bool(v) for v in row) for row in code.matrix)


def make_layout(
    url: str, right: float, top: float, ppmm: float, module_mm: float = MODULE_MM
) -> QrLayout:
    """Place the code with its module area ending `right` mm from the card's right edge."""
    px = max(1, round(module_mm * ppmm))
    module = px / ppmm  # integer pixel count per module
    m = qr_matrix(url)
    return QrLayout(matrix=m, module_mm=module, x=right - len(m) * module, y=top)
