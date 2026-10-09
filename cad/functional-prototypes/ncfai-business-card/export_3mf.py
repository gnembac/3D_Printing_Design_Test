"""3MF exports of the NCFAI card for full-colour MJF (JLC3DP PAC-HP wants 3MF with colour data).

Two variants (which one the service reads is `k.A.`: check the order preview, else use the other):

* texture : 3MF Materials Extension `texture2d`, ONE atlas PNG (front on top, back below),
            exact UV mapping - highest colour fidelity, needs a consumer that reads textures.
* vcolor  : 3MF Materials Extension `colorgroup` = per-vertex colours on a densely triangulated
            mesh (max. triangle area, boundaries unchanged) - no texture needed.

Both are ONE watertight shell (vertices merged by position, per-corner colour/UV indices).
Units mm. Texture origin = lower left (3MF spec), same as the OBJ package.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

NS_CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS_MAT = "http://schemas.microsoft.com/3dmanufacturing/material/2015/02"
REL_TEXTURE = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dtexture"
LABELS = ("front", "back", "edge")


@dataclass
class MergedMesh:
    verts: np.ndarray  # (n, 3) merged positions
    faces: np.ndarray  # (m, 3) indices into verts
    labels: np.ndarray  # (m,) 0 front / 1 back / 2 edge
    corner_uv: np.ndarray  # (m, 3, 2) uv of every corner (original per-material mapping)


def merge_mesh(verts: np.ndarray, uv: np.ndarray, groups: dict[str, np.ndarray]) -> MergedMesh:
    """Merge vertices by position; keep material label and per-corner uv for every face."""
    key = np.round(verts, 6)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    faces, labels, cuv = [], [], []
    for li, name in enumerate(LABELS):
        f = groups[name]
        if len(f) == 0:
            continue
        faces.append(inv[f])
        labels.append(np.full(len(f), li))
        cuv.append(uv[f])
    return MergedMesh(
        uniq, np.vstack(faces), np.concatenate(labels), np.vstack(cuv).reshape(-1, 3, 2)
    )


def _model_xml_head(extra_ns: bool = True) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS_CORE}" xmlns:m="{NS_MAT}">'
        '<metadata name="Title">NCFAI business card</metadata>'
        '<metadata name="Designer">NCFAI</metadata>'
        "<resources>"
    )


def _vertices_xml(v: np.ndarray) -> str:
    return (
        "<vertices>"
        + "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in v)
        + "</vertices>"
    )


def _package(
    path: Path, model: str, extra: dict[str, bytes] | None = None, rels: str | None = None
) -> None:
    ct = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" '
        'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '<Default Extension="png" ContentType="image/png"/></Types>'
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("3D/3dmodel.model", model)
        if rels:
            z.writestr("3D/_rels/3dmodel.model.rels", rels)
        for name, data in (extra or {}).items():
            z.writestr(name, data)


def write_texture_3mf(path: Path, mm: MergedMesh, front: Image.Image, back: Image.Image) -> None:
    """Texture variant with ONE texture (atlas): front on top, back below.

    Many 3MF consumers evaluate only a single texture per object, so both faces share one image
    (u unchanged, v remapped: front -> 0.5..1, back -> 0..0.5; origin lower left). Edge faces
    sample a white pixel of the front texture (card corner). One texture2dgroup, no materials.
    """
    w, h = front.size
    atlas = Image.new("RGB", (w, 2 * h), (255, 255, 255))
    atlas.paste(front.convert("RGB"), (0, 0))  # image top = v 1.0 -> front
    atlas.paste(back.convert("RGB"), (0, h))  # image bottom half -> back
    uv = mm.corner_uv.copy()  # (m, 3, 2)
    lab = mm.labels
    uv[lab == 0, :, 1] = 0.5 + 0.5 * uv[lab == 0, :, 1]
    uv[lab == 1, :, 1] = 0.5 * uv[lab == 1, :, 1]
    uv[lab == 2] = (0.002, 0.998)  # front corner pixel = white
    coords = uv.reshape(-1, 2)
    body = "".join(f'<m:tex2coord u="{u:.6f}" v="{v:.6f}"/>' for u, v in coords)
    tri = "".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}" pid="2" p1="{k}" p2="{k + 1}" p3="{k + 2}"/>'
        for k, (a, b, c) in zip(range(0, 3 * len(mm.faces), 3), mm.faces.tolist(), strict=True)
    )
    xml = (
        _model_xml_head()
        + '<m:texture2d id="1" path="/3D/Textures/atlas.png" contenttype="image/png" '
        'tilestyleu="clamp" tilestylev="clamp" filter="linear"/>'
        + f'<m:texture2dgroup id="2" texid="1">{body}</m:texture2dgroup>'
        + '<object id="3" name="ncfai-card" type="model">'
        + f"<mesh>{_vertices_xml(mm.verts)}<triangles>{tri}</triangles></mesh></object>"
        + '</resources><build><item objectid="3"/></build></model>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Target="/3D/Textures/atlas.png" Id="tex1" Type="{REL_TEXTURE}"/>'
        "</Relationships>"
    )
    buf = BytesIO()
    atlas.save(buf, "PNG", optimize=True)
    _package(path, xml, {"3D/Textures/atlas.png": buf.getvalue()}, rels)


def sample(img_arr: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Bilinear sample (u right, v up, origin lower left) -> (n, 3) uint8."""
    h, w, _ = img_arr.shape
    x = np.clip(u, 0, 1) * (w - 1)
    y = (1 - np.clip(v, 0, 1)) * (h - 1)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = np.minimum(x0 + 1, w - 1), np.minimum(y0 + 1, h - 1)
    fx, fy = (x - x0)[:, None], (y - y0)[:, None]
    p = (
        img_arr[y0, x0] * (1 - fx) * (1 - fy)
        + img_arr[y0, x1] * fx * (1 - fy)
        + img_arr[y1, x0] * (1 - fx) * fy
        + img_arr[y1, x1] * fx * fy
    )
    return np.clip(np.round(p), 0, 255).astype(np.uint8)


def vertex_colors(
    v: np.ndarray,
    faces: np.ndarray,
    labels: np.ndarray,
    front: Image.Image,
    back: Image.Image,
    w: float,
    h: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Per (vertex, material) colour; returns (colors (k,3), corner index (m,3))."""
    key = (faces * 3 + labels[:, None]).reshape(-1)
    uniq, inv = np.unique(key, return_inverse=True)
    vid, lab = uniq // 3, uniq % 3
    pos = v[vid]
    uf = (pos[:, 0] + w / 2) / w
    ub = (w / 2 - pos[:, 0]) / w
    vv = (pos[:, 1] + h / 2) / h
    colors = np.full((len(uniq), 3), 255, dtype=np.uint8)
    fa = np.asarray(front.convert("RGB"))
    ba = np.asarray(back.convert("RGB"))
    m = lab == 0
    colors[m] = sample(fa, uf[m], vv[m])
    m = lab == 1
    colors[m] = sample(ba, ub[m], vv[m])
    return colors, inv.reshape(-1, 3)


def write_vcolor_3mf(
    path: Path,
    mm: MergedMesh,
    front: Image.Image,
    back: Image.Image,
    width: float,
    height: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    v, f, lab = mm.verts, mm.faces, mm.labels  # mesh is already densely triangulated
    colors, cidx = vertex_colors(v, f, lab, front, back, width, height)
    cg = "".join(f'<m:color color="#{r:02X}{g:02X}{b:02X}"/>' for r, g, b in colors)
    tri = "".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}" pid="1" p1="{i}" p2="{j}" p3="{k}"/>'
        for (a, b, c), (i, j, k) in zip(f.tolist(), cidx.tolist(), strict=True)
    )
    xml = (
        _model_xml_head()
        + f'<m:colorgroup id="1">{cg}</m:colorgroup>'
        + '<object id="2" name="ncfai-card" type="model">'
        + f"<mesh>{_vertices_xml(v)}<triangles>{tri}</triangles></mesh></object>"
        + '</resources><build><item objectid="2"/></build></model>'
    )
    _package(path, xml)
    return v, f, lab, colors, cidx


def raster_check(
    v: np.ndarray,
    f: np.ndarray,
    lab: np.ndarray,
    colors: np.ndarray,
    cidx: np.ndarray,
    box_mm: tuple[float, float, float, float],
    width: float,
    height: float,
    ppmm: float = 20.0,
    side: int = 1,
) -> Image.Image:
    """Re-render the back faces inside `box_mm` (card coordinates, seen from behind) with the
    per-vertex colours interpolated over every triangle (Gouraud) - proves the QR survives."""
    x0, y0, x1, y1 = box_mm
    w, h = round((x1 - x0) * ppmm), round((y1 - y0) * ppmm)
    canvas = np.full((h, w, 3), 255.0)
    for i in np.where(lab == side)[0]:
        tri = v[f[i]]
        # back view mirrors x (image x = W/2 - mesh x), front view does not
        px = ((width / 2 - tri[:, 0] if side == 1 else tri[:, 0] + width / 2) - x0) * ppmm
        py = (height / 2 - tri[:, 1] - y0) * ppmm
        xa, xb = int(max(np.floor(px.min()), 0)), int(min(np.ceil(px.max()), w - 1))
        ya, yb = int(max(np.floor(py.min()), 0)), int(min(np.ceil(py.max()), h - 1))
        if xa > xb or ya > yb:
            continue
        gx, gy = np.meshgrid(np.arange(xa, xb + 1) + 0.5, np.arange(ya, yb + 1) + 0.5)
        den = (py[1] - py[2]) * (px[0] - px[2]) + (px[2] - px[1]) * (py[0] - py[2])
        if abs(den) < 1e-12:
            continue
        l0 = ((py[1] - py[2]) * (gx - px[2]) + (px[2] - px[1]) * (gy - py[2])) / den
        l1 = ((py[2] - py[0]) * (gx - px[2]) + (px[0] - px[2]) * (gy - py[2])) / den
        l2 = 1 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        if not inside.any():
            continue
        c = colors[cidx[i]].astype(float)
        rgb = l0[..., None] * c[0] + l1[..., None] * c[1] + l2[..., None] * c[2]
        region = canvas[ya : yb + 1, xa : xb + 1]
        region[inside] = rgb[inside]
    return Image.fromarray(np.clip(canvas, 0, 255).astype("uint8"))
