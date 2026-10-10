"""Parameters and validation for the personal BJCP judge badge (no CAD dependency).

All lengths in millimetres. Z levels are multiples of the layer height so that
colour changes happen exactly on layer boundaries (0.1 mm, 0.2 mm nozzle).

Colours are an ASSUMPTION derived from the *verbal* description of the BJCP mark in
its US trademark application (black / white / orange / blue / amber); no official
Pantone/hex values were found. Hex values below are estimated approximations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# estimated approximations - ASSUMPTION, not official BJCP values
COLORS_HEX: dict[str, str] = {
    "black": "#141414",
    "orange": "#F6A33A",
    "blue": "#1F4E9E",
    "white": "#F5F5F5",
    "amber": "#D98A0B",
    "green": "#5B9A2D",  # hop cone (estimated hop green)
    "counterplate": "#3A3A3A",
    "onepiece": "#C8C8C8",  # single-material variant (no colour information)
}

# Minimum embossed/engraved feature width and depth for JLC3DP MJF nylon (general MJF guide),
# manufacturer data (indicative), JLC3DP help pages, age 1-3 years -> re-verify before ordering.
PAC_HP_MIN_FEATURE = 0.8


def pac_hp_variant(p: BadgeParams) -> BadgeParams:
    """Variant for JLC3DP PAC-HP full-colour nylon (MJF): details >= 0.8 mm, floors >= 2.0 mm."""
    from dataclasses import replace

    return replace(
        p,
        base_thickness=4.2,  # floor above magnet pocket 2.0 mm (page: wall thickness 2 mm)
        plate_t=4.2,  # counter plate floor 2.0 mm
        pocket_clearance=0.5,  # page: tolerance +-0.3 mm -> worst case still >= 0.2 mm play
        small_shadow_depth=0.0,  # no groove for small text (0.4 mm would be < 0.8 mm minimum)
        hop_scales=False,  # scale lines (0.47 mm) below minimum width
        awn_width=PAC_HP_MIN_FEATURE,
        outline_width=PAC_HP_MIN_FEATURE,
        location_size=5.4,  # keeps stroke width >= 0.8 mm
    )


_BJCP_ID = re.compile(r"^[A-Z]\d{4}$")


def _is_multiple(value: float, step: float) -> bool:
    ratio = value / step
    return abs(ratio - round(ratio)) < 1e-6


@dataclass(frozen=True)
class BadgeParams:
    """Valid ranges are enforced in `validate()`."""

    first_name: str = "Gunter"
    last_name: str = "Nembach"
    bjcp_id: str = "E5689"  # without '#'
    location: str = "DE-Germany/Bavaria"
    title: str = "BEER JUDGE"
    org: str = "BJCP"

    half_width: float = 54.0  # ellipse semi-axis a  -> 108 mm overall
    half_height: float = 36.0  # ellipse semi-axis b -> 72 mm overall
    rim_width: float = 3.0
    band_half_height: float = 12.5  # blue name band, +/- from centre line

    layer_height: float = 0.1  # for 0.2 mm nozzle
    base_thickness: float = 3.0  # black back plate (holds magnet pockets)
    color_layer: float = 0.8  # orange / blue field height above base
    relief: float = 0.8  # raised text / symbols above fields
    relief_name: float = 1.2  # raised first/last name (extra step for 3D effect)
    shadow_offset: float = 0.8  # engraved drop-shadow groove offset (x:+, y:-)
    small_shadow_depth: float = 0.4  # groove depth for small text on orange (mono: 0.8)
    title_size: float = 5.2  # BEER JUDGE
    location_size: float = 5.0
    hop_scales: bool = True  # engraved scale lines on the hop cone
    awn_width: float = 0.55  # barley awns
    outline_width: float = 0.6  # black contour around hop / barley

    # magnet fastening (badge side + counter plate inside the shirt)
    magnet_d: float = 10.0  # disc magnet, e.g. N35/N42 NdFeB (data sheet: k.A.)
    magnet_h: float = 2.0
    magnet_spacing: float = 30.0  # centre-to-centre
    pocket_clearance: float = 0.3  # added to magnet diameter - ASSUMPTION, calibrate by test
    pocket_extra_depth: float = 0.2  # added to magnet height (glue)
    plate_w: float = 44.0  # counter plate
    plate_h: float = 16.0
    plate_t: float = 3.0

    lanyard_tab: bool = False  # optional tab + slot (not needed with magnets)
    tab_width: float = 18.0
    tab_height: float = 8.0
    slot_width: float = 9.0
    slot_height: float = 3.6

    edge_clearance: float = 0.8  # min distance relief to rim
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    colors: dict[str, str] = field(default_factory=lambda: dict(COLORS_HEX))

    # derived -----------------------------------------------------------------
    @property
    def inner_a(self) -> float:
        return self.half_width - self.rim_width

    @property
    def inner_b(self) -> float:
        return self.half_height - self.rim_width

    @property
    def z_field(self) -> float:
        return self.base_thickness

    @property
    def z_relief(self) -> float:
        return self.base_thickness + self.color_layer

    @property
    def z_top(self) -> float:
        return self.z_relief + max(self.relief, self.relief_name)

    @property
    def pocket_d(self) -> float:
        return self.magnet_d + self.pocket_clearance

    @property
    def pocket_depth(self) -> float:
        return self.magnet_h + self.pocket_extra_depth

    @property
    def id_display(self) -> str:
        return f"#{self.bjcp_id}"

    def validate(self) -> None:
        """Raise ValueError for invalid parameters."""
        if not _BJCP_ID.match(self.bjcp_id):
            raise ValueError(f"bjcp_id must be one letter + 4 digits, got {self.bjcp_id!r}")
        for name in ("first_name", "last_name", "location", "title", "org"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")
        ranges = {
            "half_width": (30.0, 60.0),
            "half_height": (20.0, 40.0),
            "rim_width": (1.6, 5.0),
            "band_half_height": (6.0, 14.0),
            "base_thickness": (2.0, 5.0),
            "color_layer": (0.4, 2.0),
            "relief": (0.4, 1.6),
            "relief_name": (0.4, 2.0),
            "shadow_offset": (0.4, 1.2),
            "small_shadow_depth": (0.0, 0.8),
            "title_size": (3.0, 7.0),
            "location_size": (3.0, 7.0),
            "awn_width": (0.3, 1.5),
            "outline_width": (0.3, 1.5),
            "magnet_d": (4.0, 15.0),
            "magnet_h": (1.0, 4.0),
            "pocket_clearance": (0.1, 0.6),
        }
        for name, (lo, hi) in ranges.items():
            value = getattr(self, name)
            if not lo <= value <= hi:
                raise ValueError(f"{name}={value} outside valid range [{lo}, {hi}]")
        for name in (
            "base_thickness",
            "color_layer",
            "relief",
            "relief_name",
            "small_shadow_depth",
            "pocket_depth",
            "plate_t",
        ):
            if not _is_multiple(getattr(self, name), self.layer_height):
                raise ValueError(f"{name} must be a multiple of layer_height {self.layer_height}")
        if self.base_thickness - self.pocket_depth < 0.8 - 1e-9:
            raise ValueError("floor above badge magnet pocket must be >= 0.8 mm")
        if self.plate_t - self.pocket_depth < 0.8 - 1e-9:
            raise ValueError("floor behind counter-plate magnet pocket must be >= 0.8 mm")
        if self.magnet_spacing / 2 + self.pocket_d / 2 + 3.0 > self.inner_a:
            raise ValueError("magnet pockets too close to rim")
        if self.magnet_spacing < self.pocket_d + 2.0:
            raise ValueError("magnet pockets overlap")
        wall = (self.plate_w - self.magnet_spacing - self.pocket_d) / 2
        if wall < 1.2 or (self.plate_h - self.pocket_d) / 2 < 1.2:
            raise ValueError("counter plate wall around magnet pocket must be >= 1.2 mm")
        if self.band_half_height >= self.inner_b - 12.0:
            raise ValueError("band leaves no room for upper/lower text zones")
        if self.lanyard_tab and self.slot_height + 2 * 1.6 > self.tab_height:
            raise ValueError("tab too small for slot (min 1.6 mm ligament)")
