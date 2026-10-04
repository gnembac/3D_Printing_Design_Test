"""Validate released exports before they are committed as a revision.

Checks, per file in exports/stl and exports/3mf:
  - filename matches the project naming convention
  - file is non-empty
  - mesh is manifold/watertight (only if `trimesh` is installed; otherwise
    this check is skipped and reported as `k.A.`)

This script does not replace a manual CAD review (see
templates/part-design-review-template.md) — it only catches mechanical
mistakes before export.

Usage:
    python scripts/validate_cad_exports.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from filename_convention import is_valid_filename

REPO_ROOT = Path(__file__).resolve().parent.parent
MESH_DIRS_BY_EXTENSION = {
    REPO_ROOT / "exports" / "stl": ".stl",
    REPO_ROOT / "exports" / "3mf": ".3mf",
}

try:
    import trimesh

    _HAS_TRIMESH = True
except ImportError:
    _HAS_TRIMESH = False


def check_mesh_watertight(path: Path) -> bool | None:
    """Return True/False if trimesh is available, else None (k.A.)."""
    if not _HAS_TRIMESH:
        return None
    mesh = trimesh.load(path, force="mesh")
    return bool(mesh.is_watertight)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not is_valid_filename(path.name):
        errors.append(f"{path}: filename does not match project convention")
    if path.stat().st_size == 0:
        errors.append(f"{path}: file is empty")
    watertight = check_mesh_watertight(path)
    if watertight is False:
        errors.append(f"{path}: mesh is not watertight/manifold")
    elif watertight is None:
        print(f"{path}: watertight check skipped (k.A. — trimesh not installed)")
    return errors


def main() -> int:
    all_errors: list[str] = []
    for mesh_dir, extension in MESH_DIRS_BY_EXTENSION.items():
        if not mesh_dir.exists():
            continue
        for path in sorted(mesh_dir.rglob(f"*{extension}")):
            if path.is_file():
                all_errors.extend(validate_file(path))

    if all_errors:
        print("CAD export validation FAILED:")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print("CAD export validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
