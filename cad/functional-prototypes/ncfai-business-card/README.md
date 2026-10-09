# NCFAI-Visitenkarte – 3D-gedrucktes Unikat (EXP)

**Stand:** 2026-10-09 (Rev. 9: Logo oben mittig, DOEMENS erhaben silber, BJCP vertieft, Name unten) · **Revision:** EXP (nicht freigegeben)
**Prozess/Material:** MJF, PAC-HP Nylon (Vollfarbe), Supplier CN-A (Herstellerdaten, Anhaltswerte)

## 1 Anforderungen → Umsetzung (Rev. 9)

| Anforderung | Umsetzung |
|---|---|
| 85 × 55 mm | exakt 85 × 55 mm, Ecken R4, ein Körper (eine Schale) |
| Dicke max. 2,5 mm | **Grundplatte 2,0 mm** + **0,5 mm Relief (nur Vorderseite) = 2,5 mm** nominal |
| Firmenlogo | NCFAI-Logo (flach, Farbe) **oben mittig**, darunter Farbverlauf-Linie und zentrierte Firmenzeile |
| DOEMENS BIERSOMMELIER | **erhaben** (+0,5 mm), eine Zeile über die Kartenbreite, **silber** (Verlauf #CDCDCF → #8C8C91, aus dem Doemens-Screenshot geschätzt), keine Linie |
| BJCP Beer Judge | blaue Fläche **auf der Hauptebene** (Verlauf #006898 → #004878, aus dem BJCP-Screenshot), Schrift „BJCP / BEER / JUDGE“ **weiß und vertieft** (−0,5 mm unter die Hauptebene), keine Linie |
| Name | „Gunter Nembach“ **erhaben** (navy) unten links **oberhalb** der Adresse „Heubacher Hauptstr. 33“ |
| Rückseite | unverändert: Logo mittig links, Roboterkopf oben, Mikrochip unten (flach), QR-Code rechts mit URL |
| Relief-Schrift | **DejaVu Sans Bold** (kräftigere, gleichmäßigere Striche als Liberation Sans) |

## 2 Feinheits-Regeln im Modell (Herstellerdaten Supplier CN-A, konservativ)

| Regel | Wert | Umsetzung |
|---|---|---|
| Wand | ≥ 2,0 mm | Grundplatte 2,0 mm; Gravur nur im Relief |
| Breite erhabener Stege / Gravurrillen | ≥ 0,8 mm | Filter `enforce_min_feature` (Öffnen + Schließen mit r = 0,39 mm) auf die gesamte Reliefgeometrie; Stege schmaler als 0,8 mm entfallen |
| Relief-/Gravurtiefe | CN-A-Regel 0,8 mm, MJF-Artikel 0,5 mm | **0,5 mm – Abweichung von der konservativen Regel**, weil 2,0 + 0,8 > 2,5 mm. Die DFM-Prüfung `supplier_dfm_check.py` meldet das (FAIL `detail_min`) → **DFM-Rückmeldung des Anbieters zwingend** |
| Abstand Relief ↔ Kartenrand | ≥ 3,0 mm | im Mesh-Bau geprüft |
| Kleintext (Firma, Qualifikationen, Adresse) | nur Farbdruck, **kein Relief** | Strichstärke ≈ 0,4 mm < 0,8 mm |
| Farbregistrierung | `ASSUMPTION` ± 0,3 mm | Farbe wird aus derselben Vektorgeometrie wie das Relief erzeugt; Rillengrund/Rand-Farben liegen innerhalb der Flächen |
| Kein Schrumpfungsausgleich | – | erst nach Messdaten |

### Abweichungen von den konservativen Anbieterwerten (bewusst, DFM-Rückfrage zwingend)

| Punkt | Wert hier | Anbieter (Supplier CN-A) | Folge |
|---|---|---|---|
| Relief-/Gravurtiefe | 0,5 mm | Designregel 0,8 mm, MJF-Artikel 0,5 mm | 2,0 + 0,8 > 2,5 mm |
| Breite erhabener/vertiefter Striche | ≥ 0,7 mm (Mindestfilter), Buchstaben 5,2–5,4 mm DejaVu Bold | 0,8 mm (Artikel 0,5 mm) | größere Schrift passt nicht auf die Karte |
| Restwand unter den vertieften BJCP-Buchstaben | **1,5 mm** (2,0 − 0,5) | PAC-HP-Seite 2,0 mm; MJF allgemein ≤ 50 mm: 1,5 mm | örtlich dünner als das PAC-HP-Wandminimum; alternativ BJCP-Platte erhaben + Gravur bis auf 2,0 mm (wandsicher) |

## 3 Verzug (Geometrieentscheidung)

| Maßnahme | Wirkung (nicht gemessen, k.A.) |
|---|---|
| Ebene Platte, gleichmäßig 2,0 mm, Ecken R4 | gleichmäßige Abkühlung, keine Spannungsspitzen |
| Relief nur 0,5 mm, Name + DOEMENS (ca. 7 % der Fläche), ≥ 3 mm vom Rand | begrenzte Asymmetrie des Querschnitts |
| Rückseite völlig eben | Auflagefläche |
| Löcher entfallen (`n_bubbles = 0`) | keine Perforation (optional per Parameter) |
| **Offen:** einseitiges Relief kann Verzug erhöhen | Kontrollkarte `--relief 0` (2,0 mm eben) → EX-001 |

**Zielkonflikt (Entscheidung nötig):** Toleranz ±0,3 mm → Gesamthöhe bis 2,8 mm, Grundplatte ab 1,7 mm. „Max. 2,5 mm“ gilt hier **nominal**. Strenge Alternative: Relief 0,0 (rein Farbe).

## 4 Annahmen / offen

| Punkt | Status |
|---|---|
| Firmenkürzel | **NCFAI** (vom Nutzer bestätigt; „NCAI“ war ein Tippfehler) |
| „Biersommeliere“ | geklärt: Schriftzug **DOEMENS BIERSOMMELIER** (Nutzer-Erratum) |
| Dateiformat | OBJ + MTL + 2 PNG (ZIP) trägt Verläufe als Textur. Für PAC-HP nennt der Anbieter „OBJ oder 3MF“, für Textur-OBJ ausdrücklich nur Full-Color-Resin → **vor Bestellung beim Support klären** |
| Farbtreue | sRGB-Quelle ≠ Prozessfarbe; Grün/Orange/Blau-Verläufe `k.A.` → Erstmuster |
| Schwarz der QR-Module | Abbildung beim Anbieter `k.A.`; Scantest simuliert (Unschärfe 0,25 mm, Tintenzu-/abnahme ±0,1 mm je Kante, Scan 8 px/mm: alle dekodiert, `estimated`) |
| QR-Ziel | URL fest im Druck → Weiterleitung auf der Landing Page vorsehen |
| Gewicht ≈ 9–10 g | `estimated` (Volumen 9 616 mm³ × ≈ 1,0 g/cm³, Dichte `ASSUMPTION`) |
| Raue Pulveroberfläche | Gravurschärfe/Lesbarkeit weißer Buchstaben in Navy `k.A.` → Erstmuster |

## 5 Reproduktion

Personendaten (Adresse, URL, Texte) liegen **nicht im Git**: `private/` ist ignoriert; `card_content.example.json` zeigt das Format (Felder `name`, `company`, `qualification`, `address`, `url`, `doemens`, `bjcp`).

```bash
pip install numpy pillow shapely mapbox-earcut trimesh networkx lxml segno zxing-cpp fonttools   # optional: cadquery (STEP)
python cad/functional-prototypes/ncfai-business-card/ncfai_card.py \
  --content private/ncfai-business-card/card_content.json \
  --logo private/ncfai-business-card/ncfai_logo.png \
  --out private/ncfai-business-card --date 2026-10-09 [--seed TEXT] [--relief 0]
```

Laufzeit ≈ 30 s (STEP-Export). Exit-Code 1 bei fehlgeschlagenen Prüfungen.

## 6 Prüfungen (2026-10-09)

| Prüfung | Ergebnis |
|---|---|
| STL wasserdicht, 1 Schale, 85,00 × 55,00 × 2,50 mm | bestanden |
| Flache Kontrollvariante 85 × 55 × 2,00 mm | bestanden |
| STEP erzeugt (CadQuery) | ja |
| QR-Dekodierung (5 Simulationsfälle) | bestanden |
| ruff, pytest | bestanden |
| Relief-Tiefe 0,5 mm vs. CN-A-Regel 0,8 mm | **Abweichung dokumentiert** → DFM-Rückfrage |
| Slicer-/Anbietervorschau, Farbmuster, Ebenheit, Handy-Scan am Druck | **offen** (EX-001) |

Keine Bestellung, kein Upload, keine Anfrage ohne ausdrückliche Freigabe.
