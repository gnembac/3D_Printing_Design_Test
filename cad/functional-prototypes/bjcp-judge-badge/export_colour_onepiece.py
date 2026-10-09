"""Export the fused one-shell badge with per-face colours (PLY, 3MF).

For print services that need ONE part/shell per file but accept colour data
(full-colour resin / nylon with 3MF colours). Face colours are taken from the
colour body (black/orange/blue/white/amber) whose surface the fused face lies on.

Usage (needs trimesh + rtree + numpy). --stl-dir must hold the five colour-body STLs and
BJCP_badge-onepiece-split_*.stl (= fuse_onepiece(solids, keep_faces=True) exported as STL):
    python export_colour_onepiece.py --stl-dir exports/stl --date 2026-10-09 --out <dir>
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from badge_params import COLORS_HEX  # noqa: E402

BODIES = ("black", "orange", "blue", "white", "amber")


def _rgb(hex_: str) -> tuple[int, int, int]:
    return int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)


def classify_faces(fused: trimesh.Trimesh, stl_dir: Path, tag: str) -> np.ndarray:
    """Index into BODIES for every face of `fused` (nearest colour-body surface)."""
    pts = fused.triangles_center
    dist = np.empty((len(BODIES), len(pts)))
    for i, name in enumerate(BODIES):
        body = trimesh.load(stl_dir / f"BJCP_badge-{name}_{tag}.stl")
        for lo in range(0, len(pts), 2000):  # chunked: closest_point is memory hungry
            dist[i, lo : lo + 2000] = trimesh.proximity.closest_point(body, pts[lo : lo + 2000])[1]
    return dist.argmin(axis=0)


def write_3mf(path: Path, mesh: trimesh.Trimesh, idx: np.ndarray) -> None:
    mats = "".join(f'<base name="{n}" displaycolor="{COLORS_HEX[n].upper()}FF"/>' for n in BODIES)
    vx = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in mesh.vertices)
    tr = "".join(
        f'<triangle v1="{a}" v2="{b}" v3="{c}" pid="1" p1="{k}"/>'
        for (a, b, c), k in zip(mesh.faces, idx, strict=True)
    )
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{ns}">'
        f'<resources><basematerials id="1">{mats}</basematerials>'
        '<object id="2" name="badge" type="model" pid="1" pindex="0">'
        f"<mesh><vertices>{vx}</vertices><triangles>{tr}</triangles></mesh></object></resources>"
        '<build><item objectid="2"/></build></model>'
    )
    pkg = "http://schemas.openxmlformats.org/package/2006"
    ct = (
        f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="{pkg}/content-types">'
        '<Default Extension="rels" '
        'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" '
        'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    )
    rels = (
        f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{pkg}/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stl-dir", type=Path, required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--material", default="PLA")
    ap.add_argument("--process", default="FDM")
    ns = ap.parse_args()
    tag = f"EXP_{ns.process}_{ns.material}_{ns.date}"
    fused = trimesh.load(ns.stl_dir / f"BJCP_badge-onepiece-split_{tag}.stl", process=True)
    assert fused.is_watertight and len(fused.split(only_watertight=False)) == 1
    idx = classify_faces(fused, ns.stl_dir, tag)
    ns.out.mkdir(parents=True, exist_ok=True)
    base = ns.out / f"BJCP_badge-onepiece-colour_{tag}"
    rgba = np.array([(*_rgb(COLORS_HEX[BODIES[i]]), 255) for i in idx], dtype=np.uint8)
    trimesh.Trimesh(fused.vertices, fused.faces, face_colors=rgba, process=False).export(
        base.with_suffix(".ply")
    )
    write_3mf(base.with_suffix(".3mf"), fused, idx)
    for i, n in enumerate(BODIES):
        print(f"{n:7s} faces: {(idx == i).sum()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
