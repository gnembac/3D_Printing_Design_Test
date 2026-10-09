# EX-002 – Print-in-Place-Scharnier: Spielreihe

**Stand:** 2026-10-09 · **Revision:** EXP (experimentell) · **Status:** draft (noch nicht gedruckt)

```text
Exercise-ID:            EX-002-hinge-clearance-coupon
Date:                   2026-10-09 (Entwurf); Druckdatum k.A.
Operator:               k.A.
Printer:                k.A. (eigener FDM-Drucker, Modell/Düse vor dem Druck eintragen)
Manufacturing process:  FDM (Erstdruck); MJF PAC-HP nur nach ausdrücklicher Freigabe (siehe Folge)
Material:               k.A. (Hersteller / Produkt / Charge vor dem Druck eintragen)
Learning objective:     Ab welchem Spalt c läuft ein gedrucktes Stiftscharnier frei, ohne zu verkleben
                        oder zu klappern, und wie verhält sich der gemessene Spalt zum Sollspalt?
Prerequisite skills:    Slicer-Grundlagen, Messschieber/Fühlerlehre, Dokumentation von Druckparametern
Setup (printer, material, settings): siehe Abschnitt "Protokoll"
What was tried:         k.A. (noch nicht gedruckt)
Result (measured, with units): k.A.
Takeaway / design rule learned: k.A.
Follow-up exercise or experiment: EX-003 QR-Modulgröße/Reliefkontrast; DOE-001 Scharnierspiel auf MJF PAC-HP
Status:                 draft
```

## Hypothese (Ableitung, nicht gemessen)

Bei einem Stiftscharnier mit Ø 2,5 mm Stift verklebt c = 0,3 mm im FDM-Druck häufig, c ≥ 0,5 mm
läuft frei. Der Herstellerwert für MJF (Supplier CN-A, indikativ) liegt bei ≥ 0,6 mm für bewegliche
Teile. Ob sich FDM-Ergebnisse auf MJF übertragen lassen, ist **offen** und mit diesem Coupon nicht zu
beantworten.

## Faktor- und Antworttabelle

| Größe | Typ | Wert / Skala |
|---|---|---|
| Spiel c (radial = axial) | Faktor, 6 Stufen | 0,30 / 0,40 / 0,50 / 0,60 / 0,80 / 1,00 mm |
| Druckausrichtung | konstant | Blätter flach auf dem Bett, Achse parallel Y (`ASSUMPTION`) |
| Stiftdurchmesser, Wand, Blattdicke | konstant | 2,5 / 2,5 / 2,5 mm (Quelle: `hinge_params.py`) |
| Funktionsklasse | Antwort, ordinal | 0 verklebt · 1 schwergängig · 2 frei · 3 klappert (> 5° Spiel, geschätzt) |
| Gemessener Spalt axial | Antwort, mm | Fühlerlehre, 3 Stellen je Scharnier |
| Gemessener Spalt radial | Antwort, mm | aus Bohrung − Stift (Messschieber), 2 Stellen je Scharnier |
| Öffnungswinkel frei | Antwort, ° | Winkelmesser/Foto |

## Protokoll

1. Coupon `EX002_hinge-clearance-coupon_EXP_FDM_PLA_2026-10-09.stl` (oder `.step`) aus `exports/` laden.
   Material nach Datenblatt trocknen/lagern und im Material-Record erfassen.
2. Druckparameter vollständig protokollieren (Düse, Schichthöhe, Temperaturen, Geschwindigkeit,
   Kühlung, Wände, Infill, Stützen **aus**, Brim). Keine Schrumpfkompensation.
3. Erst nach vollständigem Abkühlen bewegen. Scharniere 10× öffnen/schließen, Klasse notieren.
4. Spalte nach obiger Tabelle messen; Messgerät und Kalibrierstatus eintragen (`quality/calibration/`).
5. Rohdaten unverändert nach `data/raw/EX-002_<datum>.csv`, Auswertung nach `data/processed/`.
6. Bei Widerspruch zwischen Sollspalt und Messwert: Messwert zählt, Sollwert nicht korrigieren.

## Grenzen der Aussage

- n = 1 je Stufe: nur deskriptiv, keine Inferenz. Kritische Stufen (0,5–0,8 mm) einmal wiederholen.
- Ergebnis gilt nur für diesen Drucker, dieses Material und diese Charge.
- Keine Aussage zur Ermüdung/Lebensdauer des Scharniers.
- Der Coupon ist ein Nicht-Norm-Test.

## Dateien

| Datei | Zweck |
|---|---|
| `cad/test-specimens/ex002-hinge-clearance-coupon/hinge_params.py` | Parameter, Validierung, MJF-Regelabgleich |
| `cad/test-specimens/ex002-hinge-clearance-coupon/hinge_coupon.py` | CadQuery-Quelle (STEP + binäre STL) |
| `exports/step/EX002_hinge-clearance-coupon_EXP_FDM_PLA_2026-10-09.step` | abgeleitet |
| `exports/stl/EX002_hinge-clearance-coupon_EXP_FDM_PLA_2026-10-09.stl` | abgeleitet |
| `tests/test_ex002_hinge_params.py` | Tests der Parameter |

Geometrieprüfung (2026-10-09, CadQuery 2.8.0 / trimesh): alle 12 Körper gültig, Überlappung A/B = 0 mm³,
minimaler Abstand A–B = Sollspalt (0,30 … 1,00 mm), STL wasserdicht. Plattenmaße 100 × 68 × 9,5 mm.
Neu erzeugen: `python cad/test-specimens/ex002-hinge-clearance-coupon/hinge_coupon.py --out exports/tmp --date <datum>`.
