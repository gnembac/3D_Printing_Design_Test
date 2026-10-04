"""Generate a manifest of all released exports under exports/.

Writes data/results/export-manifest.csv with one row per file: relative
path, parsed revision/process/material/date (if the filename matches the
project convention), size in bytes, and a SHA-256 hash for traceability.

Usage:
    python scripts/generate_manifest.py
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from filename_convention import parse_filename

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORTS_DIR = REPO_ROOT / "exports"
MANIFEST_PATH = REPO_ROOT / "data" / "results" / "export-manifest.csv"
EXPORT_EXTENSIONS = {".step", ".stp", ".stl", ".3mf", ".pdf", ".dxf", ".dwg"}

FIELDNAMES = [
    "relative_path",
    "project",
    "part_number",
    "revision",
    "process",
    "material",
    "date",
    "size_bytes",
    "sha256",
]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest_rows(exports_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not exports_dir.exists():
        return rows
    for path in sorted(exports_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXPORT_EXTENSIONS:
            continue
        parsed = parse_filename(path.name)
        rows.append(
            {
                "relative_path": str(path.relative_to(exports_dir.parent)),
                "project": parsed.project if parsed else "k.A.",
                "part_number": parsed.part_number if parsed else "k.A.",
                "revision": parsed.revision if parsed else "k.A.",
                "process": parsed.process if parsed else "k.A.",
                "material": parsed.material if parsed else "k.A.",
                "date": parsed.date if parsed else "k.A.",
                "size_bytes": str(path.stat().st_size),
                "sha256": sha256_of(path),
            }
        )
    return rows


def main() -> None:
    rows = build_manifest_rows(EXPORTS_DIR)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} entries to {MANIFEST_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
