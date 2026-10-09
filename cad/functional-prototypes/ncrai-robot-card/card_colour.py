"""Textured colour 3MF for the NCRAI robot card, variant A (PAC-HP full-colour nylon, MJF).

Input: the STL written by robot_card.py (geometry only, few hundred triangles). Colour comes
from one PNG texture atlas (20 px/mm) referenced through the 3MF Materials Extension
(`texture2d` / `texture2dgroup`, per-corner UVs). The mesh stays small and the colour
resolution does not depend on the triangle size (gradient and QR modules stay sharp).

ASSUMPTION: the supplier accepts textured 3MF (Materials Extension). Not verified (k.A.) -
ask in the DFM request; fallback formats are OBJ+MTL+PNG or PLY with vertex colours.

Usage (needs numpy, trimesh, pillow, qrcode; opencv-python-headless for the QR check):
    python card_colour.py --stl <robot_card.stl> --out <dir>
Writes <stem>.3mf, atlas.png and preview PNGs (rendered from the 3MF data, not from the CAD).
"""

from __future__ import annotations

import argparse
import io
import math
import sys
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageOps

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import qr_logo  # noqa: E402
from card_params import CardParams  # noqa: E402

PX = 20  # texture pixels per mm
# ASSUMPTION: first-sample colours from the logo (measured, estimated); adjust after the sample
CYAN, MID, VIOLET = (0x2C, 0xE9, 0xFD), (0x32, 0x54, 0xA9), (0x4D, 0x1D, 0xB4)
NAVY = (0x10, 0x1A, 0x3A)
WHITE = (0xFF, 0xFF, 0xFF)
U_MIN, U_MAX, V_MIN, V_MAX = -14.5, 14.5, -0.5, 40.5  # panel texture window (panel coordinates)

Colour = tuple[int, int, int]


def gradient(t: float) -> Colour:
    """Cyan -> mid blue -> violet, t in [0, 1]."""
    t = min(1.0, max(0.0, t))
    a, b, s = (CYAN, MID, t * 2) if t < 0.5 else (MID, VIOLET, t * 2 - 1)
    return (
        round(a[0] + (b[0] - a[0]) * s),
        round(a[1] + (b[1] - a[1]) * s),
        round(a[2] + (b[2] - a[2]) * s),
    )


def _logo() -> Image.Image:
    return Image.open(HERE / "assets" / "ncrai_logo_transparent.png").convert("RGBA")


def _paste_logo(img: Image.Image, logo: Image.Image, cx: float, cy: float, w: float) -> None:
    h = w * logo.height / logo.width
    lg = logo.resize((max(1, round(w)), max(1, round(h))), Image.LANCZOS)
    img.paste(lg, (round(cx - lg.width / 2), round(cy - lg.height / 2)), lg)


# --------------------------------------------------------------------------- atlas layout
class Atlas:
    """Pixel layout of the single texture atlas (all sizes in pixels)."""

    def __init__(self, p: CardParams) -> None:
        self.p = p
        self.plate_w, self.plate_h = round(p.card_w * PX), round(p.card_h * PX)
        self.panel_w, self.panel_h = round((U_MAX - U_MIN) * PX), round((V_MAX - V_MIN) * PX)
        self.top_y0 = 0
        self.bottom_y0 = self.plate_h
        self.panel_y0 = 2 * self.plate_h
        self.patch_y0 = self.panel_y0 + self.panel_h  # solid-colour patches below the panel
        self.width = self.plate_w
        self.height = self.patch_y0 + 40
        self.patches = {"white": 0, "edge": 40, "violet": 80}  # x offsets of 40 x 40 px patches

    def plate_px(self, x: np.ndarray, y: np.ndarray, y0: int) -> tuple[np.ndarray, np.ndarray]:
        return (x + self.p.card_w / 2) * PX, y0 + (self.p.card_h / 2 - y) * PX

    def panel_px(self, u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return (u - U_MIN) * PX, self.panel_y0 + (V_MAX - v) * PX

    def patch_px(self, name: str, n: int) -> tuple[np.ndarray, np.ndarray]:
        return np.full(n, self.patches[name] + 20.0), np.full(n, self.patch_y0 + 20.0)


def build_atlas(a: Atlas) -> Image.Image:
    p = a.p
    img = Image.new("RGB", (a.width, a.height), WHITE)

    # plate top: QR code with logo (flat colour, no relief)
    qp = qr_logo.QrParams()
    full = qr_logo.build_matrix(qp.url)
    n = len(full)
    matrix = qr_logo.knock_out(full, qr_logo.logo_block(n, qp.logo_w_modules, qp.logo_h_modules))
    qr = qr_logo.render_png(matrix, qp, _logo(), px_per_module=round(qp.module_mm * PX))
    cx, cy = (p.qr_cx + p.card_w / 2) * PX, a.plate_h / 2
    img.paste(qr, (round(cx - qr.width / 2), a.top_y0 + round(cy - qr.height / 2)))

    # plate back: wordmark, drawn mirrored in world x so that it reads correctly after flipping
    _paste_logo(img, ImageOps.mirror(_logo()), cx, a.bottom_y0 + cy, 44 * PX)

    # panel front: gradient robot
    panel = Image.new("RGB", (a.panel_w, a.panel_h), WHITE)
    d = ImageDraw.Draw(panel)
    for x in range(panel.width):
        d.line([(x, 0), (x, panel.height)], fill=gradient((x / PX + U_MIN + 14.0) / 28.0))

    def pp(u: float, v: float) -> tuple[float, float]:
        return (u - U_MIN) * PX, (V_MAX - v) * PX

    d.rectangle([*pp(-12.5, 3.0), *pp(12.5, -0.5)], fill=NAVY)  # feet bar
    d.rectangle([*pp(-6.8, 25.0), *pp(6.8, 13.0)], fill=NAVY)  # chest plate
    d.rounded_rectangle([*pp(-6.2, 38.0), *pp(6.2, 31.5)], radius=PX, fill=NAVY)  # visor
    for ex in (-2.8, 2.8):  # eyes
        ex_px, ey_px = pp(ex, 34.8)
        r = 1.3 * PX
        d.ellipse(
            [ex_px - r, ey_px - r, ex_px + r, ey_px + r], fill=gradient(0.0 if ex < 0 else 1.0)
        )
    lg = _logo()
    _paste_logo(panel, lg.crop((0, 0, lg.width, 231)), *pp(0.0, 19.0), 10.5 * PX)  # dome symbol
    img.paste(panel, (0, a.panel_y0))

    draw = ImageDraw.Draw(img)  # solid patches
    for name, colour in (("edge", MID), ("violet", VIOLET)):
        x0 = a.patches[name]
        draw.rectangle([x0, a.patch_y0, x0 + 39, a.patch_y0 + 39], fill=colour)
    return img


# --------------------------------------------------------------------------- UV assignment
def face_uvs(mesh: trimesh.Trimesh, a: Atlas) -> np.ndarray:
    """(faces, 3, 2) UV coordinates (3MF convention: origin bottom-left, v up)."""
    from robot_card import panel_pose

    p = a.p
    tri = mesh.triangles  # (n, 3, 3)
    nrm = mesh.face_normals
    ang = p.relax_rad
    ey, ez = panel_pose(p)
    rel = tri - np.array([p.x_c, ey, ez])
    u = rel[..., 0]
    v = rel[..., 1] * math.cos(ang) + rel[..., 2] * math.sin(ang)
    zp = -rel[..., 1] * math.sin(ang) + rel[..., 2] * math.cos(ang)
    nu = nrm[:, 1] * -math.sin(ang) + nrm[:, 2] * math.cos(ang)
    tol = 1e-3
    top = (nrm[:, 2] > 0.999) & (np.abs(tri[..., 2] - p.t) < tol).all(1)
    bot = (nrm[:, 2] < -0.999) & (np.abs(tri[..., 2]) < tol).all(1)
    pf = (nu > 0.999) & (np.abs(zp - (p.t - p.web_t / 2)) < tol).all(1)
    pb = (nu < -0.999) & (np.abs(zp + p.web_t / 2) < tol).all(1) & (v > 0.3).all(1)
    near_panel = (
        (np.abs(u) <= 14.2).all(1)
        & (v > -0.3).all(1)
        & (v < 40.3).all(1)
        & (zp > -0.5).all(1)
        & (zp < p.t).all(1)
    )

    px = np.zeros((len(tri), 3))
    py = np.zeros((len(tri), 3))
    for k in range(3):  # default white patch, then override per class
        px[:, k], py[:, k] = a.patch_px("white", len(tri))
        m = near_panel & ~(pf | pb)
        px[m, k], py[m, k] = a.patch_px("edge", int(m.sum()))
        m = pb
        px[m, k], py[m, k] = a.patch_px("violet", int(m.sum()))
        m = top
        px[m, k], py[m, k] = a.plate_px(tri[m, k, 0], tri[m, k, 1], a.top_y0)
        m = bot
        px[m, k], py[m, k] = a.plate_px(tri[m, k, 0], tri[m, k, 1], a.bottom_y0)
        m = pf
        px[m, k], py[m, k] = a.panel_px(u[m, k], v[m, k])
    px = np.clip(px, 0.5, a.width - 0.5)  # no bleeding over the atlas border
    py = np.clip(py, 0.5, a.height - 0.5)
    return np.stack([px / a.width, 1.0 - py / a.height], axis=-1)


# --------------------------------------------------------------------------- 3MF
def write_3mf(
    path: Path, mesh: trimesh.Trimesh, uv: np.ndarray, atlas: Image.Image, title: str
) -> None:
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    nm = "http://schemas.microsoft.com/3dmanufacturing/material/2015/02"
    vx = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in mesh.vertices)
    coords = "".join(f'<m:tex2coord u="{u:.6f}" v="{v:.6f}"/>' for u, v in uv.reshape(-1, 2))
    tr = "".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}" pid="2" '
        f'p1="{3 * i}" p2="{3 * i + 1}" p3="{3 * i + 2}"/>'
        for i, (a, b, c) in enumerate(mesh.faces)
    )
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{ns}" xmlns:m="{nm}" '
        'requiredextensions="m">'
        f'<metadata name="Title">{title}</metadata>'
        "<resources>"
        '<m:texture2d id="1" path="/3D/Texture/atlas.png" contenttype="image/png" '
        'tilestyleu="clamp" tilestylev="clamp" filter="nearest"/>'
        f'<m:texture2dgroup id="2" texid="1">{coords}</m:texture2dgroup>'
        f'<object id="3" name="{title}" type="model"><mesh><vertices>{vx}</vertices>'
        f"<triangles>{tr}</triangles></mesh></object></resources>"
        '<build><item objectid="3"/></build></model>'
    )
    pkg = "http://schemas.openxmlformats.org/package/2006"
    ct = (
        f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="{pkg}/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" '
        'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '<Default Extension="png" ContentType="image/png"/></Types>'
    )
    rels = (
        f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{pkg}/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    )
    model_rels = (
        f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{pkg}/relationships">'
        '<Relationship Target="/3D/Texture/atlas.png" Id="rel1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dtexture"/></Relationships>'
    )
    buf = io.BytesIO()
    atlas.save(buf, format="PNG", optimize=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        z.writestr("3D/Texture/atlas.png", buf.getvalue())


# --------------------------------------------------------------------------- software render
def render(
    mesh: trimesh.Trimesh,
    uv: np.ndarray,
    atlas: Image.Image,
    az: float,
    el: float,
    scale: float = 12.0,
) -> tuple[Image.Image, tuple[float, float, int]]:
    """Orthographic z-buffer render sampling the atlas via the per-corner UVs.

    Returns the image and (x0, y0, height) to map world (x, screen-y) to pixels:
    px = (x - x0) * scale, py = height - (sy - y0) * scale.
    """
    a, e = math.radians(az), math.radians(el)
    rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    pts = mesh.vertices @ rz.T
    nrm = mesh.face_normals @ rz.T
    view = np.array([0.0, -math.cos(e), math.sin(e)])
    up = np.array([0.0, math.sin(e), math.cos(e)])
    sx, sy, depth = pts[:, 0], pts @ up, pts @ view
    x0, y0 = sx.min() - 3, sy.min() - 3
    w, h = int((sx.max() - x0 + 3) * scale), int((sy.max() - y0 + 3) * scale)
    out = np.full((h, w, 3), 235, dtype=np.uint8)
    zbuf = np.full((h, w), -1e9)
    tex = np.asarray(atlas)
    th, tw = tex.shape[:2]
    for fi, face in enumerate(mesh.faces):
        if nrm[fi] @ view <= 0:
            continue
        s = np.stack([(sx[face] - x0) * scale, h - (sy[face] - y0) * scale], -1)
        d = depth[face]
        lo = np.floor(s.min(0)).astype(int)
        hi = np.ceil(s.max(0)).astype(int)
        xs = np.arange(max(lo[0], 0), min(hi[0] + 1, w))
        ys = np.arange(max(lo[1], 0), min(hi[1] + 1, h))
        if len(xs) == 0 or len(ys) == 0:
            continue
        gx, gy = np.meshgrid(xs + 0.5, ys + 0.5)
        den = (s[1, 1] - s[2, 1]) * (s[0, 0] - s[2, 0]) + (s[2, 0] - s[1, 0]) * (s[0, 1] - s[2, 1])
        if abs(den) < 1e-12:
            continue
        l0 = ((s[1, 1] - s[2, 1]) * (gx - s[2, 0]) + (s[2, 0] - s[1, 0]) * (gy - s[2, 1])) / den
        l1 = ((s[2, 1] - s[0, 1]) * (gx - s[2, 0]) + (s[0, 0] - s[2, 0]) * (gy - s[2, 1])) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        z = l0 * d[0] + l1 * d[1] + l2 * d[2]
        ix, iy = gx.astype(int), gy.astype(int)
        upd = inside & (z > zbuf[iy, ix])
        if not upd.any():
            continue
        u_ = l0 * uv[fi, 0, 0] + l1 * uv[fi, 1, 0] + l2 * uv[fi, 2, 0]
        v_ = l0 * uv[fi, 0, 1] + l1 * uv[fi, 1, 1] + l2 * uv[fi, 2, 1]
        tx = np.clip((u_ * tw).astype(int), 0, tw - 1)
        ty = np.clip(((1 - v_) * th).astype(int), 0, th - 1)
        shade = 0.7 + 0.3 * float(nrm[fi] @ view)
        col = (tex[ty, tx] * shade).astype(np.uint8)
        zbuf[iy[upd], ix[upd]] = z[upd]
        out[iy[upd], ix[upd]] = col[upd]
    return Image.fromarray(out), (float(x0), float(y0), h)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stl", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ns = ap.parse_args()
    p = CardParams()
    p.validate()
    mesh = trimesh.load(ns.stl, process=True)
    if not mesh.is_watertight:
        raise SystemExit("input mesh is not watertight")
    layout = Atlas(p)
    atlas = build_atlas(layout)
    uv = face_uvs(mesh, layout)
    ns.out.mkdir(parents=True, exist_ok=True)
    stem = ns.stl.stem
    write_3mf(ns.out / f"{stem}.3mf", mesh, uv, atlas, stem)
    atlas.save(ns.out / "atlas.png", optimize=True)
    print(f"faces {len(mesh.faces)}, vertices {len(mesh.vertices)}, atlas {atlas.size}")

    top, (x0, y0, h) = render(mesh, uv, atlas, az=0, el=90, scale=PX)  # top-down, 20 px/mm
    half = round(24.6 * PX)
    cx_px, cy_px = round((p.qr_cx - x0) * PX), round(h - (0 - y0) * PX)
    crop = top.crop((cx_px - half, cy_px - half, cx_px + half, cy_px + half))
    crop.save(ns.out / "qr_from_3mf_data.png")
    got = qr_logo.decode(crop)
    print(f"QR decoded from rendered 3MF data: {got!r} -> {'OK' if got == qr_logo.URL else 'FAIL'}")
    for name, (az, el) in {
        "front": (0, 28),
        "iso": (-35, 30),
        "back": (180, 28),
        "top": (0, 90),
    }.items():
        render(mesh, uv, atlas, az, el)[0].save(ns.out / f"preview_{name}.png")
    return 0 if got == qr_logo.URL else 1


if __name__ == "__main__":
    raise SystemExit(main())
