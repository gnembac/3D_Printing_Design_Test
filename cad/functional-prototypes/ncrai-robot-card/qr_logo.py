"""QR code with an integrated centre logo for the NCRAI robot card (no CAD dependency).

All lengths in millimetres. The logo knocks out a rectangular block of centre modules; the
code stays decodable only through Reed-Solomon error correction (level H restores up to
about 30 % of the codewords, manufacturer-independent QR standard ISO/IEC 18004).

Outputs (see `main`):
- SVG in true millimetres (dark modules as rectangles, logo embedded as PNG)
- PNG preview
- CSV of the module matrix (1 = dark) for the CAD generator

Usage (needs qrcode + pillow; opencv-python-headless only for `--verify`):
    python qr_logo.py --out assets [--verify]
"""

from __future__ import annotations

import argparse
import base64
import csv
import io
from dataclasses import dataclass
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw
from qrcode.constants import ERROR_CORRECT_H

URL = "https://nc-robots-ai.com/"
# manufacturer data (Supplier CN-A, MJF): minimum embossed/engraved detail 0.8 mm (conservative);
# flat colour modules are not relief, but the module size is kept above this value anyway.
MIN_MODULE_MM = 0.8
# Measured (OpenCV Aruco decoder, version 4-H, random data-module errors, 40 trials each):
# 9x5 block (4.1 %) -> 100 % decodable up to 6 flipped modules, 13x7 (8.4 %) -> only 38 %.
# Budget is therefore capped at 5 % so that print/colour deviations stay tolerable.
MAX_LOGO_AREA_FRACTION = 0.05
DARK_HEX = "#101A3A"  # estimated: dark navy, from the NCRAI logo palette (contrast on white)
LIGHT_HEX = "#FFFFFF"


@dataclass(frozen=True)
class QrParams:
    url: str = URL
    module_mm: float = 1.2  # 41 modules incl. quiet zone = 49.2 mm (fits 54 mm panel width)
    quiet_modules: int = 4  # ISO/IEC 18004 quiet zone
    logo_w_modules: int = (
        9  # knocked-out block, centre modules (measured: 9x5 keeps >= 6 module errors)
    )
    logo_h_modules: int = 5
    logo_padding_modules: float = 0.5  # white margin between logo and code modules

    def validate(self, n_modules: int) -> None:
        if self.module_mm < MIN_MODULE_MM:
            raise ValueError(f"module_mm {self.module_mm} < {MIN_MODULE_MM} mm")
        if self.quiet_modules < 4:
            raise ValueError("quiet zone must be >= 4 modules")
        area = self.logo_w_modules * self.logo_h_modules / n_modules**2
        if area > MAX_LOGO_AREA_FRACTION:
            raise ValueError(f"logo area {area:.1%} > {MAX_LOGO_AREA_FRACTION:.0%}")
        if self.logo_w_modules >= n_modules or self.logo_h_modules >= n_modules:
            raise ValueError("logo block larger than code")


def build_matrix(url: str) -> list[list[bool]]:
    """QR matrix (True = dark) with error correction H and the smallest fitting version."""
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=0, box_size=1)
    qr.add_data(url)
    qr.make(fit=True)
    return [[bool(v) for v in row] for row in qr.get_matrix()]


def logo_block(n: int, w: int, h: int) -> tuple[int, int, int, int]:
    """(col0, row0, col1, row1) of the centred knock-out block, end exclusive."""
    col0, row0 = (n - w) // 2, (n - h) // 2
    return col0, row0, col0 + w, row0 + h


def knock_out(matrix: list[list[bool]], block: tuple[int, int, int, int]) -> list[list[bool]]:
    col0, row0, col1, row1 = block
    return [
        [False if (row0 <= r < row1 and col0 <= c < col1) else v for c, v in enumerate(row)]
        for r, row in enumerate(matrix)
    ]


def _hex_rgb(hex_: str) -> tuple[int, int, int]:
    return int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)


def render_png(
    matrix: list[list[bool]],
    p: QrParams,
    logo: Image.Image | None,
    px_per_module: int = 20,
) -> Image.Image:
    n = len(matrix)
    q = p.quiet_modules
    size = (n + 2 * q) * px_per_module
    img = Image.new("RGB", (size, size), _hex_rgb(LIGHT_HEX))
    draw = ImageDraw.Draw(img)
    dark = _hex_rgb(DARK_HEX)
    for r, row in enumerate(matrix):
        for c, v in enumerate(row):
            if v:
                x, y = (c + q) * px_per_module, (r + q) * px_per_module
                draw.rectangle([x, y, x + px_per_module - 1, y + px_per_module - 1], fill=dark)
    if logo is not None:
        col0, row0, col1, row1 = logo_block(n, p.logo_w_modules, p.logo_h_modules)
        box_w = (col1 - col0 - 2 * p.logo_padding_modules) * px_per_module
        box_h = (row1 - row0 - 2 * p.logo_padding_modules) * px_per_module
        scale = min(box_w / logo.width, box_h / logo.height)
        lw, lh = max(1, round(logo.width * scale)), max(1, round(logo.height * scale))
        resized = logo.resize((lw, lh), Image.LANCZOS)
        cx = (col0 + col1) / 2 * px_per_module + q * px_per_module
        cy = (row0 + row1) / 2 * px_per_module + q * px_per_module
        img.paste(resized, (round(cx - lw / 2), round(cy - lh / 2)), resized)
    return img


def render_svg(
    matrix: list[list[bool]], p: QrParams, logo_png: bytes | None, with_background: bool = True
) -> str:
    """SVG in true millimetres: dark modules merged to horizontal runs, optional embedded logo."""
    n = len(matrix)
    q, m = p.quiet_modules, p.module_mm
    side = (n + 2 * q) * m
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{side:g}mm" height="{side:g}mm" viewBox="0 0 {side:g} {side:g}">'
    ]
    if with_background:
        parts.append(f'<rect width="{side:g}" height="{side:g}" fill="{LIGHT_HEX}"/>')
    parts.append(f'<g fill="{DARK_HEX}">')
    for r, row in enumerate(matrix):
        c = 0
        while c < n:
            if row[c]:
                start = c
                while c < n and row[c]:
                    c += 1
                parts.append(
                    f'<rect x="{(start + q) * m:g}" y="{(r + q) * m:g}" '
                    f'width="{(c - start) * m:g}" height="{m:g}"/>'
                )
            else:
                c += 1
    parts.append("</g>")
    if logo_png is not None:
        col0, row0, col1, row1 = logo_block(n, p.logo_w_modules, p.logo_h_modules)
        pad = p.logo_padding_modules
        x, y = (col0 + pad + q) * m, (row0 + pad + q) * m
        w, h = (col1 - col0 - 2 * pad) * m, (row1 - row0 - 2 * pad) * m
        b64 = base64.b64encode(logo_png).decode()
        parts.append(
            f'<image x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'xlink:href="data:image/png;base64,{b64}"/>'
        )
    parts.append("</svg>")
    return "".join(parts)


def decode(img: Image.Image) -> str:
    """Decode with OpenCV (verification only; raises ImportError if cv2 is not installed)."""
    import cv2
    import numpy as np

    arr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    # the classic cv2.QRCodeDetector fails on clean synthetic codes; the Aruco detector reads them
    text, _, _ = cv2.QRCodeDetectorAruco().detectAndDecode(arr)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument(
        "--logo", type=Path, default=Path(__file__).parent / "assets" / "ncrai_logo_transparent.png"
    )
    ap.add_argument("--url", default=URL)
    ap.add_argument("--module-mm", type=float, default=QrParams.module_mm)
    ap.add_argument("--verify", action="store_true")
    ns = ap.parse_args()

    p = QrParams(url=ns.url, module_mm=ns.module_mm)
    full = build_matrix(p.url)
    n = len(full)
    p.validate(n)
    matrix = knock_out(full, logo_block(n, p.logo_w_modules, p.logo_h_modules))
    logo = Image.open(ns.logo).convert("RGBA")
    small = logo.resize((400, round(400 * logo.height / logo.width)), Image.LANCZOS)
    buf = io.BytesIO()
    small.save(buf, format="PNG", optimize=True)

    ns.out.mkdir(parents=True, exist_ok=True)
    (ns.out / "ncrai_qr_logo.svg").write_text(
        render_svg(matrix, p, buf.getvalue()), encoding="utf-8"
    )
    preview = render_png(matrix, p, logo)
    preview.save(ns.out / "ncrai_qr_logo_preview.png", optimize=True)
    with (ns.out / "ncrai_qr_matrix.csv").open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([[int(v) for v in row] for row in matrix])
    side = (n + 2 * p.quiet_modules) * p.module_mm
    area = p.logo_w_modules * p.logo_h_modules / n**2
    print(f"version {(n - 17) // 4}, {n}x{n} modules, side incl. quiet zone {side:g} mm")
    print(f"logo block {p.logo_w_modules}x{p.logo_h_modules} modules = {area:.1%} of code area")
    if ns.verify:
        got = decode(preview)
        print(f"decode: {got!r} -> {'OK' if got == p.url else 'FAIL'}")
        return 0 if got == p.url else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
