# JLC3DP — External Manufacturing Reference (China)

| | |
|---|---|
| Version | 1.0 |
| Status | 2026-10-08 18:17 UTC |
| Data class | **Manufacturer data** (public website), not own measured results |
| Source retrieved | 2026-10-08 (user-supplied compilation of jlc3dp.com/de help-center articles) |
| Service | JLC3DP (3D-printing service of the JLC group, Shenzhen, CN) — <https://jlc3dp.com/de> |
| Re-verify before | any RFQ, DFM review or order — the website changes without notice |

## Change log

| Version | Date / time (UTC) | Change |
|---|---|---|
| 1.0 | 2026-10-08 18:17 | Initial analysis, consolidation into design rules, material CSVs and DfM check script |

## Purpose

This folder turns a collection of JLC3DP help-center articles into reusable,
machine-readable project context for:

1. **Design constraints** for parts that may be outsourced (FDM, SLA, SLS,
   MJF, SLM, BJ, WJP) → [`design-guidelines.md`](design-guidelines.md)
2. **Material base data** (manufacturer data, kept separate from own test
   data) → [`data/material-datasheets/jlc3dp/`](../../../data/material-datasheets/jlc3dp/)
3. **Automated DfM pre-check** →
   [`scripts/jlc3dp_dfm_check.py`](../../../scripts/jlc3dp_dfm_check.py)
4. **Claude working context** — referenced from `.claude/CLAUDE.md`
   ("External manufacturing reference data").

The original `.docx` compilation is **not** committed: it contains
copyrighted images and marketing text of the service provider. Only facts
(numbers, rules) are extracted, each with a source reference.

## Source register

| ID | Article (as titled on jlc3dp.com/de) | Last updated (per source) | URL |
|---|---|---|---|
| G | Konstruktionsrichtlinien für den 3D-Druck (sections G1–G10) | 2025-06-02 | <https://jlc3dp.com/de/help/article/212-3D-Printing-Design-Guideline> |
| SLA-A | Was ist der Stereolithografie-(SLA-)3D-Druck? | 2026-01-09 | <https://jlc3dp.com/3d-printing/stereolithography> (process page) |
| ST | Unterschiede Resin-Drucke mit/ohne Oberflächenbehandlung | 2025-10-25 | <https://jlc3dp.com/de/help/article/differences-between-resin-3d-prints-with-and-without-surface-treatment> |
| CP | Unterschied Vollfarbdruck vs. Sprühlackierung | 2026-01-02 | k.A. (help-center article) |
| SLS-A | Was ist Selektives Lasersintern (SLS)? | 2026-01-08 | k.A. (help-center article) |
| MET-A | Was ist Metall-3D-Druck? | 2026-01-08 | <https://3d.jlcpcb.com/3d-printing/selective-laser-melting> (SLM page) |
| FDM-A | Was ist Fused Deposition Modeling (FDM)? | 2026-01-02 | k.A. (help-center article) |
| MJF-A | Was ist Multi Jet Fusion (MJF)? | 2026-01-09 | <https://jlc3dp.com/3d-printing/multi-jet-fusion> |
| M-* | Material pages (26 materials, see overview CSV `source_updated`) | 2025-10-25 … 2026-01-08 | e.g. <https://jlc3dp.com/help/article/200-PA12-HP-Nylon>, <https://jlc3dp.com/help/article/201-PAC-HP-Nylon> |

## Analysis

### Content structure of the source (deductive overview)

| Block | Content | Engineering value | Used in |
|---|---|---|---|
| Design guideline (G1–G10) | size, wall, details, threads, clearances, vent holes, holes, pins, special shapes, tolerances | **high** — quantitative, process-comparative | `design-guidelines.md`, rules CSV, script |
| Process articles (SLA, SLS, MJF, FDM, metal) | working principle, material families, pros/cons, per-process rule tables | medium — rule tables useful, rest is marketing | rules CSV (conflicts documented) |
| Surface / colour articles | surface treatment, full colour vs. spray paint | low–medium — process options only | `design-guidelines.md` §7 |
| Material pages (26) | price "from", lead time, tolerance, wall, size, HDT, mechanical table | **high** but with data-quality defects | overview + mechanical CSV |

### Key findings (engineering interpretation)

| # | Finding | Type | Consequence for this project |
|---|---|---|---|
| 1 | HDT values are given at **different loads** (0.45 MPa vs. 1.8 MPa). Example MJF PA11-HP: 185 °C @ 0.45 MPa but **54 °C @ 1.82 MPa**. | from data | Never rank materials by HDT without the load level. Compare at 1.8 MPa for structural parts. |
| 2 | FDM data mostly **without print orientation**; only PLA/ASA state "X-Y". No Z (inter-layer) values for FDM materials. | from data | FDM service values are not design values for Z-loaded parts (`CLAUDE.md`: no claim without orientation). Z capability must come from own tests. |
| 3 | MJF PA12S-HP is **near-isotropic** (tensile 45 MPa XY / 43 MPa Z), but elongation drops 12 % → 5 % in Z. | from data | Powder-bed processes are preferable where load direction is uncertain; ductility is still orientation-dependent. |
| 4 | General tolerance ±0.3 mm (≤ 100 mm) / ±0.4 % (> 100 mm) for FDM/SLS/MJF/SLM, ±0.2 mm / ±0.3 % for SLA. | from data | ≈ ISO 286 IT13–IT14 (estimated). Functional fits (bearings, press fits, sealing) need post-machining or must be treated as CTQ with own measurement. |
| 5 | Holes generally **shrink**; hole tolerance ±0.3–0.5 mm; SLA dimensions **drift** by up to 0.2 mm / 0.2 % within 7 days. | from data | Measure SLA parts after ≥ 7 days of conditioning; specify reaming allowance for precise holes. |
| 6 | Published rules **contradict each other** in several places (FDM min. hole 1.5 vs. 3.0 mm, FDM detail 0.8 vs. 1.0 mm, max. sizes). | from data | Rules CSV keeps every value with its source; the **conservative** value governs in the check script. |
| 7 | Only ASA is declared outdoor/UV-suitable; all SLA/WJP resins are explicitly **not** suitable for outdoor, sunlight, UV or elevated temperature (HDT 46–80 °C). | from data | SLA/WJP only for indoor models, fixtures, visual prototypes. |
| 8 | "X Resin" is a **random** resin allocation printed on varying machines. | from data | **Excluded** from experiments and functional parts — not traceable (violates material-record rule). |
| 9 | Prices are "from" list prices (USD); lead times are build times without shipping/customs. | from data | Use only for rough cost-model plausibility, never as quotation. Re-check date. |
| 10 | Several mechanical tables contain unit, standard-number or row-shift errors (see below). | from data | Flagged in CSV (`quality_flag`); values reconstructed only as `ASSUMPTION`. |
| 11 | Test standards mix ASTM, ISO and **GB/T** (Chinese national standards). | from data | Values from different standards are not directly comparable; see `docs/standards-and-test-methods.md`. |

### Data-quality defects found in the source

| Material | Defect | Handling in CSV |
|---|---|---|
| FDM ASA | tensile strength unit "%", flexural strength unit "kJ/m²", Charpy listed with ASTM D790/ISO 178 | unit corrected to MPa (`unit_corrected`), method `k.A.` (`method_conflict`) |
| FDM ABS, PA12-CF | "Izod" labelled with ISO 179 (= Charpy) | `method_conflict` |
| FDM PLA | Charpy listed with ASTM D256 (= Izod) | `method_conflict` |
| MJF PA11-HP | property table rows shifted by one line | reconstructed, `table_shift` + `ASSUMPTION` |
| MJF PA12S-HP | two impact values without orientation | `incomplete`, XY/Z as `ASSUMPTION` |
| WJP Full Color Resin | tensile modulus 5.79 MPa (implausible), "90A" under Shore D | value set `k.A.`, `implausible` |
| SLA Imagine Black | tensile strength in comparison table identical to flexural strength; impact in kJ/m² while other resins use J/m; flexural modulus with ASTM D638M | `suspect_copy`, `unit_check`, `method_error` |
| SLA 9600, Grey | standard typos (D2241, D1549-97a), CTE unit "°C" | corrected, flagged |
| SLS 3301PA | HDT with "ISO 78-1", flexural values with ISO 527-1 | `method_error` |
| Sizes | max./min. build size differs between size table, process article and material page (ABS, PLA, ASA, PA12-CF, TPU, 1172 Pro, PAC, 8228) | material-page value used, conflict noted |
| 8001 resin, SLM 316L | listed, but no datasheet in the source | `incomplete`, `k.A.` |

## How to use (humans and Claude)

| Task | Use | Do not |
|---|---|---|
| Design a part that may be outsourced | `design-guidelines.md` + `python scripts/jlc3dp_dfm_check.py ...` | treat a PASS as supplier approval — DFM feedback from the supplier is still mandatory |
| Pick candidate materials | overview CSV + `docs/material-selection-matrix.md` | compare HDT/impact values across different loads/standards |
| Mechanical sizing | manufacturer values as **starting point** with explicit safety factor and orientation note | quote them as own results or as ISO/ASTM-compliant properties of *our* parts |
| Cost model | `price_from_usd` as lower bound, dated | use as quotation |
| China manufacturing package | rules + `CLAUDE.md` "China supplier rules" + spec §13 | upload, order or contact the supplier without explicit user approval |

## Maintenance

- On each re-check, create new dated CSV files (`..._YYYY-MM-DD.csv`), never
  overwrite the previous ones; update `RULES_CSV` in the script and this
  change log.
- Record discrepancies between JLC3DP data and own measurements in
  `docs/reports/`, not in these files.
