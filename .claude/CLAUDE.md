# CLAUDE.md — 3D Print Design & Test (Learning Project)

## Project purpose

This repository is an engineering **learning project** for 3D printing: it
builds practical, reproducible, scientifically documented skill through
small exercises, full DoE experiments, and parametric part development.
It is intended to end up as the public GitHub repository
[`gnembac/3D_Printing_Design_Test`](https://github.com/gnembac/3D_Printing_Design_Test).

Primary goals:

- Build practical experience with FDM/FFF and optional external manufacturing.
- Progress skills deliberately: calibration → dimensional accuracy → mechanical
  testing → functional parts → supplier packages.
- Compare geometry, print orientation, material, process parameters and cost.
- Use Design of Experiments (DoE), measurement plans and statistical analysis.
- Generate traceable manufacturing packages for Europe and China.
- Maintain engineering-quality documentation and reproducibility, written so
  a third party reading the public repo can follow and repeat the work.

Background knowledge base (German, source specification for this ruleset):
[`010_Instructions_Know_How/`](../010_Instructions_Know_How/). When the two
disagree, this file (`CLAUDE.md`) is authoritative for day-to-day work.

## Mandatory working principles

- Treat all CAD source files, raw measurement data and approved drawings as controlled engineering artifacts.
- Never overwrite raw measurement data.
- Never alter an approved revision without creating a new revision.
- Mark assumptions explicitly as `ASSUMPTION`.
- Mark unavailable information as `k.A.`.
- Mark derived, non-measured values as `estimated`.
- Distinguish clearly between:
  1. manufacturer data,
  2. literature data,
  3. calculated values,
  4. own measured results.
- Do not claim a mechanical property without stating material, process, print orientation, specimen geometry and test method.
- Do not represent non-standard tests as ISO- or ASTM-compliant tests.
- Do not use STL as the only master representation for functional parts.
- Prefer parametric source CAD plus STEP; export STL and 3MF only as derived files.

## Safety and scope

- Do not design or approve safety-critical, medical, pressure-bearing,
  lifting, fire-safety, road-legal, aviation, electrical-safety or
  human-protection parts without a dedicated validation and compliance plan.
- For uncertain load cases, state that engineering validation is required.
- Do not make unverified claims about CE, REACH, RoHS, food contact,
  biocompatibility or regulatory compliance.
- No external ordering, supplier communication, file upload, email,
  quotation acceptance, payment, repository publishing or cloud upload
  without explicit user approval.

## Exercises vs. experiments

This is a learning project, so artifacts come in two weights. Both are
version-controlled and documented; only the rigor differs.

| | **Exercise** (`exercises/`) | **Experiment** (`experiments/`) |
|---|---|---|
| Purpose | Build or practice one specific skill | Answer a DoE-style engineering question with interacting factors |
| Scope | Single factor or fixed setup | Multiple factors, screening/factorial/response-surface design |
| Required artifacts | Learning objective, short protocol, result, one takeaway | Hypothesis, protocol, factor table, response-variable table, measurement plan, raw data, analysis, report with limitations |
| Statistical rigor | Descriptive only | Descriptive + inferential where assumptions are documented |
| Naming | `EX-NNN-<slug>` | `DOE-NNN-<slug>` |

Every exercise record states, at minimum:

```text
Exercise-ID:
Learning objective:
Prerequisite skills:
Setup (printer, material, settings):
What was tried:
Result (measured, with units):
Takeaway / design rule learned:
Follow-up exercise or experiment:
```

Promote an exercise to a full experiment as soon as more than one factor
needs to be varied to explain the result, or the result will inform a
functional part.

## Source of truth and revisions

```text
cad/parametric/                 parametric source models (CadQuery/FreeCAD/OpenSCAD)
cad/test-specimens/             coupon and test-coupon source models
cad/functional-prototypes/      functional part source models
cad/assemblies/                 assembly source models
exports/step/                   released STEP files
exports/stl/                    released STL files (derived only)
exports/3mf/                    released 3MF files (derived only)
exports/drawings/                technical drawings (PDF/DXF)
slicer-profiles/fdm/            FDM slicer profiles
slicer-profiles/sla/            SLA/MSLA/DLP slicer profiles
slicer-profiles/external-manufacturing/
exercises/EX-NNN-<slug>/        single-skill learning exercises
experiments/DOE-NNN-<slug>/     full DoE experiments
data/raw/                       raw measurements (never overwritten)
data/processed/                 cleaned and derived datasets
data/material-datasheets/       manufacturer datasheets, unmodified
data/measurements/              structured measurement logs
data/results/                   final analysis outputs
scripts/                        CAD generation, DoE, analysis, cost-model scripts
notebooks/                      exploratory analysis notebooks
bom/                            bills of material
quality/inspection-plans/
quality/calibration/            measurement-tool calibration records
quality/nonconformities/
docs/project-charter.md         scope, goals, constraints
docs/literature-review.md       sources and prior art
docs/standards-and-test-methods.md  ISO/ASTM references actually used
docs/material-selection-matrix.md   candidate materials per use case
docs/manufacturing-guidelines-eu-china.md
docs/risk-register.md
docs/experimental-protocols/    protocols for experiments and exercises
docs/reports/                   result reports
docs/suppliers/                 supplier packages (keep public-repo rules below)
docs/reference/                 background knowledge base, original specification
templates/                      protocol/report/RFQ/design-review templates
```

Use this revision convention:

- R00 = concept / not released
- R01, R02, ... = controlled engineering revisions
- EXP = experimental / not production released
- REL = released after explicit user approval

Use this filename convention:

`[project]_[part-number]_[revision]_[process]_[material]_[YYYY-MM-DD].[extension]`

Example:

`DOE003_warping-coupon_R02_FDM_ASA_2026-10-04.step`

## CAD rules

- Use millimetres as the native unit.
- Build all test coupons and functional parts parametrically.
- Document all parameters, units, defaults and valid ranges.
- Validate CAD geometry before export:
  - closed/manifold solid
  - no self-intersections
  - no zero-thickness walls
  - no inverted normals in mesh export
  - correct units
  - correct orientation
- Prefer STEP AP214 or AP242 for supplier exchange.
- Export binary STL only for compatibility.
- Prefer 3MF for printable build definitions when supported.
- Do not apply shrinkage compensation until measurement data supports it.
- Keep XY and Z shrinkage compensation separate.
- Treat print orientation as a controlled experimental factor.

## Experimental rules

For each experiment, create:

1. A hypothesis.
2. A protocol.
3. A factor table.
4. A response-variable table.
5. A measurement plan.
6. A raw-data file.
7. An analysis script or notebook.
8. A report with conclusions and limitations.

Use DoE where multiple factors may interact.

Typical factors:

- material
- material condition / drying
- nozzle temperature
- bed temperature
- chamber temperature
- layer height
- line width
- nozzle diameter
- speed
- cooling
- wall count
- infill percentage
- infill pattern
- print orientation
- annealing
- post-processing

Typical response variables:

- X/Y/Z dimensional deviation
- warping / flatness
- mass
- print time
- material cost
- surface quality
- tensile response
- flexural response
- compressive response
- layer adhesion
- creep
- environmental aging

Randomize test order where practical.
Block experiments by printer, material batch, print date and operator when relevant.
Use repeat specimens for critical comparisons.

## Material data rules

Maintain one material record per manufacturer, product, color and batch where possible.

Record:

- manufacturer
- product name
- batch or lot
- color
- filament diameter
- drying condition
- storage condition
- density
- Tg
- Tm
- HDT
- tensile strength
- tensile modulus / Young's modulus
- elongation at break
- flexural properties
- impact properties
- moisture absorption
- UV resistance
- chemical resistance
- print temperature range
- bed temperature range
- source and date

All manufacturer values must be stored separately from own test data.

## DoE and statistics rules

- Start with screening experiments before optimization.
- Use fractional factorial or Plackett-Burman designs for screening.
- Use full factorial designs where interaction effects are important.
- Use response-surface methods only after identifying relevant factors.
- Randomize run order where possible.
- Include center points and repetitions when suitable.
- Use ANOVA only when assumptions and sample size are documented.
- Report sample size, mean, standard deviation, confidence interval where possible.
- Do not infer universal material properties from one printer or one batch.

## China supplier rules

For every China manufacturing package, include:

- revision-controlled STEP file
- STL or 3MF as required
- PDF drawing with CTQ markings
- material specification and approved alternatives
- process specification
- surface and post-processing requirements
- quality control plan
- packaging instruction
- supplier RFQ template
- DFM response form
- change-control requirement
- first-article inspection requirement
- Golden Sample requirement for serial production

Do not approve:

- material substitution
- color substitution
- recycled-content change
- filler-content change
- printer/process change
- print orientation change
- post-processing change
- site change
- subcontractor change
- packaging change

without explicit written approval.

## External manufacturing reference data (Supplier CN-A)

Published design rules and material data of an online 3D-printing service
in China (anonymized as **Supplier CN-A**) are consolidated as
**manufacturer data, indicative values (Anhaltswerte) only**:

- Analysis, source register, data-quality defects:
  [`docs/reference/supplier-cn-a/README.md`](../docs/reference/supplier-cn-a/README.md)
- DfAM quick reference per process (FDM, SLA, SLS, MJF, SLM, BJ, WJP):
  [`docs/reference/supplier-cn-a/design-guidelines.md`](../docs/reference/supplier-cn-a/design-guidelines.md)
- Machine-readable data: `data/material-datasheets/supplier-cn-a/*.csv`
- DfM pre-check: `python scripts/supplier_dfm_check.py <PROCESS> --max-dim <mm> ...`

Rules when using it:

- Use these files when a part may be outsourced, when choosing between
  FDM/SLA/SLS/MJF/metal, or when an RFQ/manufacturing package is prepared.
- Label every value taken from them as manufacturer data (Supplier CN-A, source
  date); never present them as own results or as properties of our parts.
- Respect `quality_flag`: do not use `implausible`, `suspect_copy` or
  `not_traceable` values; state `ASSUMPTION` for `table_shift` values.
- Compare HDT only at the same load level; compare impact values only for
  the same method (Izod/Charpy, notched/unnotched, unit).
- FDM service values without orientation are not design values for
  Z-loaded parts.
- Where rules conflict, the conservative value governs.
- "X Resin" (random material) is excluded from experiments and
  functional parts.
- A passing DfM pre-check is not supplier approval; DFM feedback from the
  supplier remains mandatory (see "China supplier rules").
- Indicative values only: confirm by supplier DFM feedback and own
  measurements before any design or acceptance decision.
- Keep the supplier anonymized: no company name, URL, list price or
  quotation in the repository.
- Website data changes: re-verify before any RFQ and store re-checks as new
  dated files. No upload, quotation request or order without explicit user
  approval.

## GitHub repository conventions

This repository is intended to go public. Apply these rules before anything
is committed or pushed:

- Never commit personal addresses, phone numbers, bank details, supplier
  contact persons, negotiated prices, or NDA-covered content. Anonymize or
  omit supplier names in `docs/suppliers/` unless the user explicitly
  approves publishing them.
- Never commit `.env`, `secrets/`, API keys, or credentials (see Code quality).
- Large binary exports (STL/3MF, photos, measurement scans) belong under
  `exports/`, `data/`, or a Git LFS track if the repo grows large — do not
  bloat the default clone. Flag this to the user as `ASSUMPTION` if no LFS
  config exists yet.
- Root `README.md` must explain: what the project is, the directory
  structure, how to reproduce an experiment, and links to
  `docs/experimental-protocols/` and the license.
- Licensed under the Apache License 2.0 (`LICENSE`, as chosen on GitHub
  repo creation). Do not propose or scaffold a different license without
  explicit user approval.
- Use Conventional-Commits-style messages (`feat:`, `fix:`, `docs:`,
  `data:`, `exp:`) only when the user explicitly asks for a commit — never
  commit automatically.
- Do not add, change, or push a remote, and never run `git push`, without
  explicit user approval for that specific action.

## Code quality

- Use Python 3.12 or the project-defined version.
- Add type hints for new Python code.
- Keep functions small and testable.
- Use `ruff format` and `ruff check`.
- Add tests for calculations, geometry parameter validation and data transformations.
- Do not commit API keys, passwords, supplier credentials or personal information.
- Never read, print or commit `.env`, `secrets/`, private keys or credentials.

## Required commands

Before completing a code task:

```bash
ruff format .
ruff check .
pytest -q
```

The same checks run in GitHub Actions (`.github/workflows/ci.yml`, plus
`python scripts/check_repo_hygiene.py`); a pull request is only mergeable
with green CI. Releases are published by pushing a tag `REL-*`
(`.github/workflows/release.yml`) — create such a tag only with explicit
user approval.

Before exporting released CAD:

```bash
python scripts/validate_cad_exports.py
python scripts/generate_manifest.py
```

## Expected response format

When asked to create or modify a part:

1. State assumptions and missing information.
2. Define function and load case.
3. Recommend process and material candidates.
4. Define parametric model variables.
5. State DfAM constraints and risks.
6. Propose DoE if parameter uncertainty is material.
7. Generate source CAD and derived exports.
8. Create or update the protocol and revision record.
9. Provide validation commands and expected artifacts.

When asked to design an **exercise** instead of a full experiment, use the
lighter exercise record format from "Exercises vs. experiments" above
instead of the full DoE response format.

When asked to analyze data:

1. Preserve raw data.
2. Validate units and missing values.
3. Describe cleaning decisions.
4. Separate descriptive statistics from inferential claims.
5. Generate reproducible analysis code.
6. State uncertainty and limitations.
