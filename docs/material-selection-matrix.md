# Material Selection Matrix

Decision matrix for material candidates per use case. Keep manufacturer
data, literature data and own measured results in clearly separate columns
(see `CLAUDE.md` "Mandatory working principles").

| Material | Morphology | Typical fit | Key risks | Manufacturer source (indicative values) | Own test data |
|---|---|---|---|---|---|
| PLA | amorphous–semi-crystalline | prototypes, dimensional accuracy | brittleness, heat resistance | Supplier CN-A FDM PLA: 59 MPa / 2600 MPa (XY), HDT 53 °C (load k.A.) | k.A. |
| PETG | amorphous | robust all-round parts | creep, stringing | k.A. | k.A. |
| ABS | amorphous | functional prototypes, housings | warping, fumes | Supplier CN-A FDM ABS: 28.8 MPa / 1847 MPa (orientation k.A.), HDT 98 °C @ 1.8 MPa | k.A. |
| ASA | amorphous | outdoor / UV-exposed parts | warping | Supplier CN-A FDM ASA: 43.8 MPa / 2379 MPa (XY), HDT 97.8 °C (load k.A.) | k.A. |
| PA12 | semi-crystalline | tough functional parts | moisture uptake, shrinkage | Supplier CN-A MJF PA12S-HP: 45 / 43 MPa (XY / Z); MJF PA12-HP HDT 175 °C @ 0.45 MPa | k.A. |
| PA11 | semi-crystalline | snap fits, ductile parts | moisture uptake | Supplier CN-A MJF PA11-HP: 52 MPa, 50 % elongation (`ASSUMPTION`, table shift), HDT 54 °C @ 1.82 MPa | k.A. |
| PA12-CF | semi-crystalline, fibre-filled | stiff brackets, fixtures | anisotropy, abrasive, low elongation | Supplier CN-A FDM PA12-CF: 69.3 MPa / 3748 MPa, 2.9 %, HDT 105 °C @ 1.8 MPa | k.A. |
| TPU 95A / PEBA 85A | elastomer | seals, dampers, bumpers | buckling, dimensional control | Supplier CN-A: TPU 95A; PEBA 21 MPa, 600 % | k.A. |
| SLA resins (standard/engineering) | thermoset | fine detail, smooth fixtures, visual models | brittleness, UV, HDT 46–80 °C, dimensional drift | Supplier CN-A: 8228 62.4 MPa; 9600 55 MPa; CBY HDT 72–80 °C | k.A. |
| 316L (BJ / SLM) | metal | small metal functional parts | warp > 50 mm (BJ), cost | Supplier CN-A BJ-316L: 561 MPa UTS, 219 MPa yield, 50 % | k.A. |

External-service data (Supplier CN-A) and the full list of 26 service materials:
`data/material-datasheets/supplier-cn-a/` and `docs/reference/supplier-cn-a/` (manufacturer
data, status 2026-10-08; check `quality_flag` before use).
