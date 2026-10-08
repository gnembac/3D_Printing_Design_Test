# JLC3DP material and design-rule data (manufacturer data)

Status: 2026-10-08 18:17 UTC — source and analysis: [`docs/reference/jlc3dp/`](../../../docs/reference/jlc3dp/README.md)

**Data class: manufacturer data.** Never mix with own measured results
(`data/raw/`, `data/measurements/`). Values are as published by JLC3DP;
corrections are flagged, never silent.

| File | Content | Key |
|---|---|---|
| `jlc3dp_materials_overview_2026-10-08.csv` | one row per material: process, colour, price from (USD), lead time, tolerance, wall, build size, HDT + load, outdoor suitability | `material_id` |
| `jlc3dp_mechanical_properties_2026-10-08.csv` | long format: one row per material × property × orientation/condition, with test method | `material_id`, `property`, `orientation`, `condition` |
| `jlc3dp_design_rules_2026-10-08.csv` | DfM rules per process, used by `scripts/jlc3dp_dfm_check.py` | `process`, `rule_id`, `applies_to_size_max_mm` |

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
  register in `docs/reference/jlc3dp/README.md`.
- New retrieval → new dated files; old files stay unchanged.
