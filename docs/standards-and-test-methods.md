# Standards and Test Methods

Reference list of standards actually applied in this project's experiments.
Do not claim ISO/ASTM compliance for a test that deviates from the standard
— mark it `Screening test, not standard-compliant` instead
(see `CLAUDE.md` "Mandatory working principles").

| Property | Preferred standard/method | Used in |
|---|---|---|
| Tensile test, plastics | ISO 527-1 / ISO 527-2 or ASTM D638 | |
| Flexural test | ISO 178 or ASTM D790 | |
| Compression test | ISO 604 or ASTM D695 | |
| Impact strength | ISO 179 / ISO 180 or ASTM D256 | |
| HDT | ISO 75 or ASTM D648 | |
| Vicat softening | ISO 306 | |
| Density | ISO 1183 | |
| Water absorption | ISO 62 | |
| Additive manufacturing — terminology | ISO/ASTM 52900 | |
| Additive manufacturing — design | ISO/ASTM 52910 | |

## Standards encountered in external manufacturer data

Supplier datasheets (e.g. Supplier CN-A, `docs/reference/supplier-cn-a/`) mix ASTM, ISO
and Chinese national standards (GB/T). Values measured under different
standards or load levels are **not directly comparable**.

| Property | GB/T standard seen | Closest ISO / ASTM | Note |
|---|---|---|---|
| Tensile | GB/T 1040(.2) | ISO 527-2 / ASTM D638 | |
| Flexural | GB/T 9341 | ISO 178 / ASTM D790 | |
| Charpy impact | GB/T 1043(.1) | ISO 179-1 | not equal to Izod (ISO 180 / ASTM D256) |
| HDT | GB/T 1634.2 | ISO 75-2 / ASTM D648 | always state load: 0.45 vs 1.8 MPa |
| Shore hardness | GB/T 2411 | ISO 868 / ASTM D2240 | |
