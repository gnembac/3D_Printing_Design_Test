import sys
from pathlib import Path

import pytest

CARD_DIR = (
    Path(__file__).resolve().parent.parent / "cad" / "functional-prototypes" / "ncrai-robot-card"
)
sys.path.insert(0, str(CARD_DIR))

import qr_logo  # noqa: E402


def test_matrix_is_version_4_with_level_h() -> None:
    matrix = qr_logo.build_matrix(qr_logo.URL)
    assert len(matrix) == 33
    assert all(len(row) == 33 for row in matrix)


def test_default_params_valid_and_fit_panel_width() -> None:
    p = qr_logo.QrParams()
    p.validate(33)
    assert (33 + 2 * p.quiet_modules) * p.module_mm <= 54.0


@pytest.mark.parametrize(
    "bad",
    [
        {"module_mm": 0.5},
        {"quiet_modules": 2},
        {"logo_w_modules": 13, "logo_h_modules": 7},
    ],
)
def test_invalid_params_rejected(bad: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        qr_logo.QrParams(**bad).validate(33)


def test_knock_out_clears_only_the_centre_block() -> None:
    full = qr_logo.build_matrix(qr_logo.URL)
    block = qr_logo.logo_block(33, 9, 5)
    ko = qr_logo.knock_out(full, block)
    col0, row0, col1, row1 = block
    assert not any(ko[r][c] for r in range(row0, row1) for c in range(col0, col1))
    changed = sum(
        a != b for ra, rb in zip(full, ko, strict=True) for a, b in zip(ra, rb, strict=True)
    )
    assert changed <= 9 * 5


def test_svg_has_true_mm_size() -> None:
    p = qr_logo.QrParams()
    svg = qr_logo.render_svg(qr_logo.build_matrix(qr_logo.URL), p, None)
    assert 'width="49.2mm"' in svg


def test_logo_code_decodes() -> None:
    pytest.importorskip("cv2")
    from PIL import Image

    p = qr_logo.QrParams()
    full = qr_logo.build_matrix(p.url)
    ko = qr_logo.knock_out(full, qr_logo.logo_block(33, p.logo_w_modules, p.logo_h_modules))
    logo = Image.open(CARD_DIR / "assets" / "ncrai_logo_transparent.png").convert("RGBA")
    assert qr_logo.decode(qr_logo.render_png(ko, p, logo)) == p.url
