# 3D_Printing_Design_Test

[![CI](https://github.com/gnembac/3D_Printing_Design_Test/actions/workflows/ci.yml/badge.svg)](https://github.com/gnembac/3D_Printing_Design_Test/actions/workflows/ci.yml)

Learning 3D Printing - Design - Construction - Materials

Engineering **learning project** for reproducible, scientifically
documented 3D-printing experiments and parametric part development
(FDM/FFF primary; SLA, SLS, MJF, DMLS/SLM and binder jetting optional).

Repository: [`gnembac/3D_Printing_Design_Test`](https://github.com/gnembac/3D_Printing_Design_Test)

## What this is

A progression of small **exercises** and full **DoE experiments** that
build FDM/FFF printing and Design-for-Additive-Manufacturing (DfAM) skill
step by step — printer calibration → dimensional accuracy/warping →
mechanical properties (tensile/compression/layer adhesion) → functional
parts → traceable manufacturing packages for own printers and external
(EU/China) manufacturing.

All working rules (documentation standards, DoE conventions, revision
scheme, safety/scope limits, supplier rules, GitHub conventions) are
defined in [`.claude/CLAUDE.md`](.claude/CLAUDE.md). The original, more
detailed German specification this project is based on lives in
[`docs/reference/project-specification-de.md`](docs/reference/project-specification-de.md).

External-manufacturing reference (anonymized China service "Supplier CN-A", indicative values only): design rules per
process, material data and a DfM pre-check — see
[`docs/reference/supplier-cn-a/`](docs/reference/supplier-cn-a/README.md).

## Repository structure

```text
cad/                  parametric source models (CadQuery/FreeCAD/OpenSCAD)
exports/              released STEP/STL/3MF/drawings (derived, never hand-edited)
slicer-profiles/      versioned slicer profiles per printer/material/process
exercises/            single-skill learning exercises (EX-NNN-<slug>)
experiments/          full DoE experiments (DOE-NNN-<slug>)
data/                 raw measurements, processed data, datasheets, results
scripts/              CAD generation, DoE, analysis, manifest/validation scripts
notebooks/            exploratory analysis
bom/                  bills of material
quality/              inspection plans, calibration records, nonconformities
docs/                 charter, literature, standards, risk register, reports, suppliers
templates/            exercise/experiment/report/RFQ/design-review templates
```

Every directory has its own `README.md` explaining its purpose.

## How to reproduce an experiment or exercise

1. Read the protocol in `docs/experimental-protocols/` (experiments) or the
   exercise record in `exercises/EX-NNN-<slug>/` (exercises).
2. Open the parametric CAD source in `cad/`; do not start from an STL.
3. Use the matching slicer profile from `slicer-profiles/`.
4. Record raw measurements into `data/raw/` — never edit raw data in place.
5. Run the analysis script/notebook referenced in the report.
6. Read the report in `docs/reports/` for the resulting design rule and
   stated limitations.

Before exporting released CAD:

```bash
python scripts/validate_cad_exports.py
python scripts/generate_manifest.py
```

Before completing a code change:

```bash
ruff format .
ruff check .
pytest -q
```

DfM pre-check against Supplier CN-A published rules (manufacturer data):

```bash
python scripts/supplier_dfm_check.py FDM --max-dim 80 --wall 2.0 --hole-dia 3.2
```

## CI/CD

| Workflow | Trigger | Checks / action |
|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | push to `main`/`claude/**`, pull request, manual | `ruff format --check`, `ruff check`, `pytest` (Python 3.12 + 3.13), CAD export validation incl. watertight check, export manifest up to date, public-repo hygiene (no secrets files, no files > 10 MB) |
| [`release.yml`](.github/workflows/release.yml) | tag `REL-*` (explicit release approval) | all checks again, then GitHub Release with `exports/` + manifest as ZIP |

Local setup: `pip install -r requirements-dev.txt`.

## Status and scope

This is a personal learning project, not a certified engineering source.
Mechanical property claims always state material, process, print
orientation, specimen geometry and test method; non-standard tests are
marked as screening tests, not ISO/ASTM-compliant. No safety-critical,
medical, pressure-bearing, lifting, fire-safety, road-legal, aviation,
electrical-safety or human-protection parts are designed or approved here
without a dedicated validation and compliance plan.

## License

Licensed under the [Apache License 2.0](LICENSE).
