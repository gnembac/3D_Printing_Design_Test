# NCFAI-Visitenkarte – 3D-gedrucktes Unikat (EXP)

**Stand:** 2026-10-09 (Rev. 12: 3MF-Export Vollfarbe für JLC3DP) · **Revision:** EXP (nicht freigegeben)
**Prozess/Material:** MJF, PAC-HP Nylon (Vollfarbe), Supplier CN-A (Herstellerdaten, Anhaltswerte)

## 1 Anforderungen → Umsetzung (Rev. 11)

| Anforderung | Umsetzung |
|---|---|
| 85 × 55 mm | exakt 85 × 55 mm, Ecken R4, ein Körper (eine Schale) |
| Dicke max. 2,5 mm | **Grundplatte 2,0 mm** + **0,5 mm Relief (nur Vorderseite) = 2,5 mm** nominal |
| Firmenlogo | NCFAI-Logo (flach, Farbe, 25 mm breit) oben mittig, darunter Farbverlauf-Linie und zentrierte Firmenzeile |
| DOEMENS / BJCP | zwei **zentrierte** Schriftzüge untereinander, ohne Spiegelstrich, 4,2 mm (eine Stufe kleiner als 4,7 mm): „DOEMENS BIERSOMMELIER“ **erhaben**, silber (Verlauf #CDCDCF → #8C8C91); „BJCP BEER JUDGE“ **vertieft** (−0,5 mm), Boden im BJCP-Blau (#006898 → #004878) |
| Name | „**Gunter**“ (6,8 mm) eine Stufe größer als „Nembach“ (5,6 mm), erhaben, navy, über dem Adressblock |
| Rückseite | Logo mittig links, Roboterkopf oben, Mikrochip unten (flach), QR-Code rechts mit URL |
| Relief-Schrift | DejaVu Sans Bold (kräftigere, gleichmäßigere Striche) |

### Abweichungen von den konservativen Anbieterwerten (bewusst, DFM-Rückfrage zwingend)

| Punkt | Wert hier | Anbieter (Supplier CN-A) | Folge |
|---|---|---|---|
| Relief-/Gravurtiefe | 0,5 mm | Designregel 0,8 mm, MJF-Artikel 0,5 mm | 2,0 + 0,8 > 2,5 mm |
| Breite erhabener/vertiefter Striche und Zwischenräume | ≥ 0,5 mm (Mindestfilter = MJF-Artikelwert), Buchstaben 4,2–6,8 mm DejaVu Bold | 0,8 mm (Artikel 0,5 mm) | bei 0,6–0,7 mm zerfiel die gravierte Schrift (Buchstaben-Zwischenräume werden gefüllt); größere Schrift passt nicht auf die Karte |
| Restwand unter der vertieften BJCP-Schrift | **1,5 mm** (2,0 − 0,5) | PAC-HP-Seite 2,0 mm; MJF allgemein ≤ 50 mm: 1,5 mm | örtlich dünner als das PAC-HP-Wandminimum; alternativ BJCP-Platte erhaben + Gravur bis auf 2,0 mm (wandsicher) |

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

## 7 3MF für JLC3DP (Vollfarbe, PAC-HP)

Anbieter-Vorgabe (JLC3DP-Hilfe, Stand 29.12.2023, vor Bestellung prüfen): Datei **als 3MF** und **mit allen Farbdaten**, sonst
wird **grau** gefertigt; je Datei **ein** Teil/eine Schale. Das Skript erzeugt zwei 3MF-Varianten (beide: eine wasserdichte
Schale, Einheit mm, ohne Stützen/Zusatzkörper). **Welche der Anbieter einliest, ist `k.A.`** → zuerst Textur-3MF hochladen,
in der Bestellvorschau auf Farbe prüfen, sonst Vertex-Farb-3MF.

| Datei (`…_EXP_MJF_PAC-HP_2026-10-09.3mf`) | Farbträger | Größe | Prüfung |
|---|---|---|---|
| `NCFAI-card_unikat001-texture_…` | 3MF-Materials-Extension `texture2d`, **eine** Atlas-Textur 3 400 × 4 400 px (1 016 dpi; Vorderseite oben, Rückseite unten) mit exakter UV-Zuordnung | ≈ 2,6 MB, 64 020 Dreiecke | wasserdicht, 1 Schale (trimesh); Rück-/Vorderseite unabhängig aus der Datei nachgerendert |
| `NCFAI-card_unikat001-vcolor_…` | `colorgroup` = Farbe je Ecke (Vertex), Netz fein trianguliert (≤ 0,02 mm², Randpunkte ≤ 0,4 mm) | ≈ 20 MB, 830 324 Dreiecke | wasserdicht, 1 Schale; QR im Rückrender (Farbinterpolation) lesbar |

- **Rev. 12a:** Eine erste Fassung enthielt zwei getrennte Texturen (Vorder-/Rückseite); manche Viewer werten nur eine Textur je Objekt aus und zeigten die Vorderseite auch hinten. Daher jetzt ein gemeinsamer Atlas (Kanten-Flächen nutzen ein weißes Pixel).
- Die flache Kontrollkarte (`--relief 0`) erzeugt dieselben zwei Varianten mit Suffix `-flat`.
- Grenzen: Vertex-Farben lösen kleine Schrift (2,6 mm Adresse) gröber auf als die Textur (≈ 0,15 mm Dreieckskante); Farbtreue
  sRGB → MJF-Prozessfarbe `k.A.` (Erstmuster); `requiredextensions` ist bewusst nicht gesetzt, damit Leser ohne
  Materials-Extension die Geometrie noch laden (dann grau).
- Dateien enthalten Personendaten (Adresse, URL) → bleiben in `private/` (nicht im Git).
- Reproduktion: `ncfai_card.py … [--dense-area 0.02] [--no-3mf]` (zusätzlich `triangle`, `lxml`, `networkx` installieren).
