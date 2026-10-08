# Supplier CN-A material and design-rule data (manufacturer data)

Status: 2026-10-08 18:24 UTC (anonymized supplier, no price data) — source and analysis: [`docs/reference/supplier-cn-a/`](../../../docs/reference/supplier-cn-a/README.md)

**Data class: manufacturer data — indicative values (Anhaltswerte) only.** Never mix with own measured results
(`data/raw/`, `data/measurements/`). Values are as published by Supplier CN-A;
corrections are flagged, never silent.

| File | Content | Key |
|---|---|---|
| `cn-a_materials_overview_2026-10-08.csv` | one row per material: process, colour, lead time, tolerance, wall, build size, HDT + load, outdoor suitability | `material_id` |
| `cn-a_mechanical_properties_2026-10-08.csv` | long format: one row per material × property × orientation/condition, with test method | `material_id`, `property`, `orientation`, `condition` |
| `cn-a_design_rules_2026-10-08.csv` | DfM rules per process, used by `scripts/supplier_dfm_check.py` | `process`, `rule_id`, `applies_to_size_max_mm` |

## Conventions

- `k.A.` = not stated in source; `n/a` = not applicable.
- `value_min` = `value_max` for single values; ranges as published; `sd` =
  standard deviation where published.
- `orientation`: `XY`, `Z`, `XYZ`, `k.A.` (FDM: not stated → do not use
  for Z-loaded design), `n/a` (isotropic-assumed resins).
- `quality_flag`: `ok`, `conflict`, `unit_corrected`, `unit_check`,
  `method_conflict`, `method_error`, `table_shift`, `implausible`,
  `suspect_copy`, `incomplete`, `not_traceable`, `derived`.
- Rule `source` IDs (G2 … G10C, FDM-A, MJF-A, M-…) map to the source
  register in `docs/reference/supplier-cn-a/README.md`.
- New retrieval → new dated files; old files stay unchanged.
