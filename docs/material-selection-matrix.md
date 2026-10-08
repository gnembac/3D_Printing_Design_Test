# Material Selection Matrix

Decision matrix for material candidates per use case. Keep manufacturer
data, literature data and own measured results in clearly separate columns
(see `CLAUDE.md` "Mandatory working principles").

| Material | Morphology | Typical fit | Key risks | Manufacturer source | Own test data |
|---|---|---|---|---|---|
| PLA | amorphous–semi-crystalline | prototypes, dimensional accuracy | brittleness, heat resistance | JLC3DP FDM PLA: 59 MPa / 2600 MPa (XY), HDT 53 °C (load k.A.) | k.A. |
| PETG | amorphous | robust all-round parts | creep, stringing | k.A. | k.A. |
| ABS | amorphous | functional prototypes, housings | warping, fumes | JLC3DP FDM ABS: 28.8 MPa / 1847 MPa (orientation k.A.), HDT 98 °C @ 1.8 MPa | k.A. |
| ASA | amorphous | outdoor / UV-exposed parts | warping | JLC3DP FDM ASA: 43.8 MPa / 2379 MPa (XY), HDT 97.8 °C (load k.A.) | k.A. |
| PA12 | semi-crystalline | tough functional parts | moisture uptake, shrinkage | JLC3DP MJF PA12S-HP: 45 / 43 MPa (XY / Z); MJF PA12-HP HDT 175 °C @ 0.45 MPa | k.A. |
| PA11 | semi-crystalline | snap fits, ductile parts | moisture uptake | JLC3DP MJF PA11-HP: 52 MPa, 50 % elongation (`ASSUMPTION`, table shift), HDT 54 °C @ 1.82 MPa | k.A. |
| PA12-CF | semi-crystalline, fibre-filled | stiff brackets, fixtures | anisotropy, abrasive, low elongation | JLC3DP FDM PA12-CF: 69.3 MPa / 3748 MPa, 2.9 %, HDT 105 °C @ 1.8 MPa | k.A. |
| TPU 95A / PEBA 85A | elastomer | seals, dampers, bumpers | buckling, dimensional control | JLC3DP: TPU 95A; PEBA 21 MPa, 600 % | k.A. |
| SLA resins (standard/engineering) | thermoset | fine detail, smooth fixtures, visual models | brittleness, UV, HDT 46–80 °C, dimensional drift | JLC3DP: 8228 62.4 MPa; 9600 55 MPa; CBY HDT 72–80 °C | k.A. |
| 316L (BJ / SLM) | metal | small metal functional parts | warp > 50 mm (BJ), cost | JLC3DP BJ-316L: 561 MPa UTS, 219 MPa yield, 50 % | k.A. |

External-service data (JLC3DP) and the full list of 26 service materials:
`data/material-datasheets/jlc3dp/` and `docs/reference/jlc3dp/` (manufacturer
data, status 2026-10-08; check `quality_flag` before use).
