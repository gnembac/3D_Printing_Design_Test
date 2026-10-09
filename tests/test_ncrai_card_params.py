import math
import sys
from dataclasses import replace
from pathlib import Path

import pytest

CARD_DIR = (
    Path(__file__).resolve().parent.parent / "cad" / "functional-prototypes" / "ncrai-robot-card"
)
sys.path.insert(0, str(CARD_DIR))

from ncrai_card_params import SILHOUETTE, CardParams  # noqa: E402


def test_defaults_valid() -> None:
    CardParams().validate()


def test_closed_card_is_thinner_than_4_mm() -> None:
    assert CardParams().closed_thickness < 4.0


def test_window_fills_plate_height_with_symmetric_margin() -> None:
    p = CardParams()
    _, _, y0, y1 = p.window
    assert y0 == pytest.approx(-p.card_h / 2 + p.margin)
    assert y1 == pytest.approx(p.card_h / 2 - p.margin)
    assert p.margin >= 2.0  # PAC-HP wall rule (manufacturer data, indicative)


def test_window_clears_the_qr_area() -> None:
    p = CardParams()
    assert p.window[0] > p.qr_cx + 24.6


def test_web_arc_geometry_and_strain() -> None:
    p = CardParams()
    assert p.r_mid * p.relax_rad == pytest.approx(p.web_len)
    assert p.strain == pytest.approx(p.web_t * math.radians(p.relax_deg) / (2 * p.web_len))
    assert p.strain <= 0.05  # assumed elastic limit, ASSUMPTION


def test_only_the_film_hinge_deviates_from_mjf_rules() -> None:
    findings = CardParams().mjf_findings()
    assert len(findings) == 1
    assert "film hinge" in findings[0]


def test_steeper_opening_raises_strain() -> None:
    assert CardParams(relax_deg=100.0).strain > CardParams(relax_deg=55.0).strain
    assert any("strain" in f for f in CardParams(relax_deg=100.0).mjf_findings())


def test_silhouette_fits_inside_window_with_gap() -> None:
    p = CardParams()
    x0, x1, _, _ = p.window
    assert max(abs(r[0]) for r in SILHOUETTE) + p.gap <= (x1 - x0) / 2 + 1e-9
    assert p.web_w <= p.panel_w


@pytest.mark.parametrize(
    "bad",
    [{"relax_deg": 0.0}, {"relax_deg": 150.0}, {"web_t": 3.0}, {"web_len": 30.0}, {"qr_cx": 10.0}],
)
def test_invalid_parameters_rejected(bad: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        replace(CardParams(), **bad).validate()
