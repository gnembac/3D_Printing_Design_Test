# JLC3DP Design Guidelines — Consolidated (DfAM Quick Reference)

| | |
|---|---|
| Version | 1.0 |
| Status | 2026-10-08 18:17 UTC |
| Data class | Manufacturer data (JLC3DP), source IDs see [`README.md`](README.md#source-register) |
| Machine-readable | [`jlc3dp_design_rules_2026-10-08.csv`](../../../data/material-datasheets/jlc3dp/jlc3dp_design_rules_2026-10-08.csv) |
| Check script | `python scripts/jlc3dp_dfm_check.py <PROCESS> --max-dim <mm> [--wall ...]` |

Values are **supplier minimums for simple geometry**, not guaranteed
capabilities and not own results. Where the source contradicts itself,
the conservative value is marked **bold** and governs.

## 1. Build envelope

| Process | Material | Max. L×W×H (mm) | Min. (mm) |
|---|---|---|---|
| SLA | Ledo 6060, 9600, Black, JLC Black, 8001, CBY | 780×780×530 | 5×5×5 / 10×2×2 |
| SLA | Imagine Black, Grey, 8228 | 580×580×380 (8228: 390) | 5×5×5 / 10×2×2 |
| WJP | Full Color Resin | 380×330×230 | 5×5×5 / 10×2×2 |
| MJF | PA12-HP, PA12S-HP, PA11-HP | 370×276×360 | 5×5×5 / 10×2×2 |
| MJF | PAC-HP (full colour) | 190×223×248 (size table: 320×175×225) | 5×5×5 / 10×2×2 |
| SLS | 3201 PA-F, 3301PA | 350×350×400 | 5×5×5 / 10×2×2 |
| SLS | Precimid 1172 Pro | 300×300×590 (size table: 250×250×590) | 5×5×5 / 10×2×2 |
| SLM | 316L | 390×290×390 | 5×5×5 / 10×2×2 |
| BJ | 316L | 100×100×100 | 5×5×5 / 10×2×2 |
| FDM | ABS, PA12-CF | 580×480×480 (size table PA12-CF: 250×250×300) | **30×30×15** (table: 30×30×10) |
| FDM | PLA, ASA, TPU, PEBA | 250×250×250–300 | **30×30×15** |

**Design rule:** FDM parts < 30 mm are not accepted — combine small parts on a
carrier or switch to SLA/MJF/SLS.

## 2. Minimum wall thickness by part size (G2)

| Process | ≤ 5 mm | ≤ 10 mm | ≤ 50 mm | ≤ 100 mm | ≤ 200 mm |
|---|---|---|---|---|---|
| SLA | 0.5 | 0.8 | 1.0 | 1.5 | 2.0 |
| MJF | 1.0 | 1.2 | 1.5 | 2.0 | 2.0 |
| SLS | 1.0 | 1.2 | 1.5 | 2.0 | 2.0 |
| SLM | 1.5 | 1.5 | 1.5 | 2.0 | 2.5 |
| FDM | – | – | 1.6 | 2.0 | 2.5 |

- Bosses, locators, snap fits, fastening features: **≥ 1.5 mm** (all processes).
- Material pages: FDM recommended 1.6 mm (min. 1.2 mm); SLA 0.8 mm; MJF/SLS
  1.0 mm; PAC-HP 2.0 mm; BJ-316L > 1.0 mm.
- Parts > 200 mm: not specified (k.A.) — the script extrapolates the
  200 mm value; treat as `ASSUMPTION`.

**Comparison with own FDM start values** (spec §7.1, 0.4 mm nozzle): own
"general part" 1.2–2.0 mm vs. JLC3DP 1.6–2.5 mm by size. For supplier
packages the JLC3DP value governs; for own printers own measured data
governs once available.

## 3. Embossed / engraved details (G3)

| SLA | MJF | SLS | FDM | SLM |
|---|---|---|---|---|
| 0.8 | **0.8** (MJF article: 0.5) | 0.8 | **1.0** (guideline: 0.8) | 1.0 |

Values = minimum depth **and** width in mm.

## 4. Threads (G4)

| | SLA | MJF | SLS | FDM | SLM |
|---|---|---|---|---|---|
| Min. pitch | 0.5 mm | 0.6 mm | 0.6 mm | 1.0 mm | n/a — tap after printing |
| Helix angle | 30° | 30° | 30° | 30° | n/a |

- Smallest recommended printed thread: **M6**. Clearance must follow §5.
- Precise holes/threads: add machining allowance and tap/ream yourself.
- Project rule (spec §7.2) still applies: prefer heat-set inserts, nut traps
  or through-bolts over loaded printed plastic threads.

## 5. Clearances (G5)

| Gap | SLA | MJF | SLS | FDM | SLM |
|---|---|---|---|---|---|
| Parts printed for later assembly | 0.2 | 0.2–0.4 | 0.2–0.4 | 0.5 | 0.5 |
| Moving / print-in-place parts | 0.5 | 0.6 | 0.6 | 0.5 | 1.0 |

Values in mm, valid for simple structures only (dovetail, ball-socket).
Long sliding lengths and large contact areas need more — validate with a
clearance coupon (see §10).

## 6. Vent / escape holes (G6)

- Hollow parts need at least one escape hole; min. Ø **2.5 mm**.
- Ø < 3.0 mm → at least **two** holes (resin/powder must drain; trapped
  resin can crack the part later).
- Supports inside cavities cannot be removed unless the opening is large.
- Oil-spray/painted parts: min. hole Ø 2.0 mm (clogging).

## 7. Holes and pins (G7, G8)

| | SLA | MJF | SLS | FDM | SLM |
|---|---|---|---|---|---|
| Min. hole Ø | 1.0 | 1.5 | 1.5 | **3.0** (guideline: 1.5) | 1.5 |
| Max. hole depth / Ø | 3 | 3 | 3 | 3 | 3 |
| Min. pin Ø | 1.0 | 2.0 | 2.0 | **2.5** (guideline: 2.0) | 2.0 |
| Max. pin height / Ø | 2 (Ø1: H = 1 mm) | 2 | 2 | 2 | 2 |

Ratios are `estimated` — derived from the published Φ/h and D/H tables
(Φ 1.0 → h 1–3 mm, Φ 1.5 → 1.5–4.5 mm, Φ 2.0 → 2–6 mm; D 2.0 → H 2–4 mm,
D 3.0 → H 3–6 mm).

## 8. Tolerances (G10)

| Process | ≤ 100 mm | > 100 mm | Holes | Drift over time |
|---|---|---|---|---|
| SLA | ±0.2 mm | ±0.3 % | ±0.3 mm | +0.15 mm/0.15 % (1–3 d), +0.2 mm/0.2 % (3–7 d) |
| MJF | ±0.3 mm | ±0.4 % | ±0.3 mm | k.A. |
| SLS | ±0.3 mm | ±0.4 % | ±0.3 mm | k.A. |
| FDM | ±0.3 mm | ±0.4 % | ±0.4 mm | k.A. |
| SLM | ±0.3 mm | ±0.4 % | ±0.5 mm (316L internal: up to −0.5 mm) | k.A. |
| BJ 316L | ±0.3 mm / ±0.4 % (≤ 50 mm) | ±1.3 % (> 50 mm) | k.A. | k.A. |
| WJP | ±0.2 mm | ±0.3 % | k.A. | k.A. |

Conditions: no warp, no oil-spray or paint. Holes generally come out
**undersize**; thicker hole walls shrink more.

**Design rules derived (`estimated`):**

1. Tolerance class ≈ ISO 286 IT13–IT14 → no direct functional fits.
2. Put CTQ dimensions on the drawing; plan reaming/machining allowance
   (e.g. +0.3–0.5 mm stock on Ø for precision bores — `ASSUMPTION`, verify
   with a coupon).
3. SLA: measure after ≥ 7 days conditioning; record conditioning time.
4. BJ-316L: keep features ≤ 50 mm where accuracy matters.

## 9. Process / material selection guide (from manufacturer data)

| Requirement | First choice | Reason (manufacturer data) | Caveat |
|---|---|---|---|
| Outdoor / UV | FDM ASA | only material declared UV-suitable; HDT 97.8 °C | load level of HDT k.A.; FDM anisotropy |
| Heat > 80 °C, low load | MJF PA12-HP / PA11-HP, SLS 1172 Pro | HDT 175–185 °C @ 0.45 MPa | PA11: only 54 °C @ 1.82 MPa |
| Stiffness | FDM PA12-CF | E 3748 MPa, flexural 3532 MPa | elongation 2.9 %, orientation k.A. |
| Snap fits, living hinges, ductility | MJF PA11-HP | elongation 50 % (reconstructed) | verify — table shift in source |
| Isotropic structural parts | MJF PA12S-HP | 45/43 MPa XY/Z | Z elongation 5 % |
| Fine detail, smooth surface | SLA 8228, 9600 | 62.4 / 55 MPa, Shore D 81–83 | HDT 53–59 °C, no UV, dimensional drift |
| Higher-temperature resin | SLA CBY | HDT 72–80 °C | tensile only 25–30 MPa |
| Humid environment | SLA Imagine Black, Ledo 6060 | manufacturer claim | HDT 46 / 56 °C |
| Elastomer | FDM TPU 95A, PEBA 85A | PEBA elongation 600 %, −70 °C | wall ≥ 1.6 mm |
| Metal, small | BJ-316L (≤ 100 mm) | 561 MPa UTS, 50 % elongation, cheaper than SLM | warp > 50 mm |
| Metal, larger | SLM 316L | 390×290×390 mm | no datasheet in source (k.A.) |
| Colour models | WJP Full Color, MJF PAC-HP | integrated colour | WJP not outdoor; PAC $17 from |
| Experiments / traceability | any **except** X Resin | — | X Resin = random material |

Surface options (ST, CP): resin parts with or without surface treatment
(sanding, polishing, coating, painting); spray painting is single-colour
only (gloss or matte), applied manually — not an industrial colour finish.

## 10. Suggested follow-up exercises / experiments

| ID (proposed) | Type | Question |
|---|---|---|
| EX-nnn-clearance-coupon-fdm | Exercise | Do the FDM gaps (0.5 mm assembly / moving) hold on the own printer? Step 0.2–0.8 mm. |
| EX-nnn-hole-undersize-fdm | Exercise | Measure hole undersize vs. Ø (1.5–10 mm) and wall thickness; compare with ±0.4 mm. |
| DOE-nnn-outsourced-vs-own | Experiment | Same coupon in own FDM vs. JLC3DP FDM/MJF/SLA: dimensional deviation, mass, cost, orientation (requires explicit approval before any order). |
