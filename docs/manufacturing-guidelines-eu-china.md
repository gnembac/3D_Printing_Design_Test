# Manufacturing Guidelines — EU / China

Operative summary; full rulebook is
`docs/reference/project-specification-de.md` §13 ("Spezifische Richtlinien
für chinesische 3D-Druck-Fertiger") and §13.13 (EU compliance).

## EU

- Determine early whether CE marking, RoHS, or REACH apply before placing
  parts on the EU market.
- The importer, not the supplier, is generally responsible for conformity —
  a supplier declaration does not replace an own check.
- No unverified CE/REACH/RoHS/food-contact/biocompatibility claims
  (see `CLAUDE.md` "Safety and scope").

## China suppliers

- No requirement is binding unless it is in the revision-controlled
  manufacturing package (not email/chat/screenshots).
- English only, SI units, `.` decimal separator, no vague terms
  ("high strength", "good surface", "tight fit", ...).
- Mandatory package structure, DFM feedback, Golden Sample process, AQL by
  defect class, and change-control text — see reference document §13.3–§13.11.
- No material/color/filler/process/orientation/site/subcontractor/packaging
  substitution without written approval (see `CLAUDE.md` "China supplier rules").

## Reference service: JLC3DP

Published DfM rules and material data of JLC3DP are consolidated in
`docs/reference/jlc3dp/` (design guidelines per process, source register,
data-quality defects) and `data/material-datasheets/jlc3dp/`. Run
`python scripts/jlc3dp_dfm_check.py` as a pre-check before preparing a
package. A pre-check does not replace the supplier's DFM response; general
tolerances (±0.2–0.4 mm) are not suitable for functional fits — mark CTQs.

No external ordering, supplier communication, quotation acceptance, or
payment without explicit user approval.
