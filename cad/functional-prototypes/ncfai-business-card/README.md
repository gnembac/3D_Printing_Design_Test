# NCFAI-Visitenkarte – 3D-gedrucktes Unikat (EXP)

**Stand:** 2026-10-09 (Rev. 3: Relief, Hopfendolde, Logo-Rückseite, QR-Code) · **Revision:** EXP (nicht freigegeben)
**Prozess/Material:** MJF, PAC-HP Nylon (Vollfarbe), Supplier CN-A (Herstellerdaten, Anhaltswerte)

## 1 Anforderungen → Umsetzung

| Anforderung | Umsetzung |
|---|---|
| 85 × 55 mm | exakt 85 × 55 mm, Ecken R4, ein Körper (eine Schale) |
| Dicke max. 2,5 mm | **Grundplatte 2,0 mm** (= Wandminimum PAC-HP) **+ 0,5 mm Relief = 2,5 mm** nominal; `card_params.py` erzwingt es |
| Schrift **erhaben und vertieft** | *Erhaben:* Name „Gunter / Nembach“ (Strich ≈ 1,1 mm). *Vertieft:* „DOEMENS“ und „BJCP“ als erhabene Kapseln mit **eingravierten** Buchstaben (Gravur reicht bis auf die Grundplatte, nie darunter → Wand bleibt 2,0 mm) |
| Hopfendolde (grün, weiblich) statt Rundformen | Dolde als Relief: Hochbrakteen als erhabene Schuppen, **Rillen 0,85 mm** dazwischen (Gravurwirkung), Stiel; Rillengrund dunkelgrün, Schuppen hellgrün→grün. Form pro Seed leicht anders (Unikat) |
| Rückseite: Logo | NCFAI-Logo (transparent, auf Weiß gerendert) links oben, darunter `UNIKAT No. <Hash>` |
| QR-Code auf Landing Page | rechts, 29 × 29 Module à 1,2 mm = 34,8 mm, ECC Q, Ruhezone 4 Module, Schwarz auf Weiß, URL im Klartext darunter |
| Feine Details für 3D-Druck-Kompetenz | Detailregeln siehe 2; Relief, Gravur, Rillen, Hopfenschuppen = sichtbarer Nachweis |
| Unikat | Seed → Hopfenschuppen (Lage, Größe, Neigung, Biegung, Stiel), Bläschenmuster Rückseite, Kennung. Gleicher Seed = gleiche Karte |
| Wenig Verzug | siehe 3 |

## 2 Feinheits-Regeln im Modell (Herstellerdaten Supplier CN-A, konservativ)

| Regel | Wert | Umsetzung |
|---|---|---|
| Wand | ≥ 2,0 mm | Grundplatte 2,0 mm; Gravur nur im Relief |
| Breite erhabener Stege / Gravurrillen | ≥ 0,8 mm | Filter `enforce_min_feature` (Öffnen + Schließen mit r = 0,39 mm) auf die gesamte Reliefgeometrie; Stege schmaler als 0,8 mm entfallen |
| Relief-/Gravurtiefe | CN-A-Regel 0,8 mm, MJF-Artikel 0,5 mm | **0,5 mm – Abweichung von der konservativen Regel**, weil 2,0 + 0,8 > 2,5 mm. Die DFM-Prüfung `supplier_dfm_check.py` meldet das (FAIL `detail_min`) → **DFM-Rückmeldung des Anbieters zwingend** |
| Abstand Relief ↔ Kartenrand | ≥ 3,0 mm | im Mesh-Bau geprüft |
| Kleintext (Firma, Bildunterschriften, Adresse) | nur Farbdruck, **kein Relief** | Strichstärke ≈ 0,4 mm < 0,8 mm |
| Farbregistrierung | `ASSUMPTION` ± 0,3 mm | Farbe wird aus derselben Vektorgeometrie wie das Relief erzeugt; Rillengrund/Rand-Farben liegen innerhalb der Flächen |
| Kein Schrumpfungsausgleich | – | erst nach Messdaten |

## 3 Verzug (Geometrieentscheidung)

| Maßnahme | Wirkung (nicht gemessen, k.A.) |
|---|---|
| Ebene Platte, gleichmäßig 2,0 mm, Ecken R4 | gleichmäßige Abkühlung, keine Spannungsspitzen |
| Relief nur 0,5 mm, ca. 20 % der Fläche, ≥ 3 mm vom Rand | begrenzte Asymmetrie des Querschnitts |
| Rückseite völlig eben | Auflagefläche |
| Löcher entfallen (`n_bubbles = 0`) | keine Perforation (optional per Parameter) |
| **Offen:** einseitiges Relief kann Verzug erhöhen | Kontrollkarte `--relief 0` (2,0 mm eben) → EX-001 |

**Zielkonflikt (Entscheidung nötig):** Toleranz ±0,3 mm → Gesamthöhe bis 2,8 mm, Grundplatte ab 1,7 mm. „Max. 2,5 mm“ gilt hier **nominal**. Strenge Alternative: Relief 0,0 (rein Farbe).

## 4 Annahmen / offen

| Punkt | Status |
|---|---|
| Firmenkürzel | „NCAI“ → `ASSUMPTION` Tippfehler, **NCFAI** gedruckt |
| „Biersommeliere“ | `ASSUMPTION` Tippfehler → „Biersommelier“ |
| Dateiformat | OBJ + MTL + 2 PNG (ZIP) trägt Verläufe als Textur. Für PAC-HP nennt der Anbieter „OBJ oder 3MF“, für Textur-OBJ ausdrücklich nur Full-Color-Resin → **vor Bestellung beim Support klären** |
| Farbtreue | sRGB-Quelle ≠ Prozessfarbe; Grün/Orange/Blau-Verläufe `k.A.` → Erstmuster |
| Schwarz der QR-Module | Abbildung beim Anbieter `k.A.`; Scantest simuliert (Unschärfe 0,25 mm, Tintenzu-/abnahme ±0,1 mm je Kante, Scan 8 px/mm: alle dekodiert, `estimated`) |
| QR-Ziel | URL fest im Druck → Weiterleitung auf der Landing Page vorsehen |
| Gewicht ≈ 9–10 g | `estimated` (Volumen 9 616 mm³ × ≈ 1,0 g/cm³, Dichte `ASSUMPTION`) |
| Raue Pulveroberfläche | Gravurschärfe/Lesbarkeit weißer Buchstaben in Navy `k.A.` → Erstmuster |

## 5 Reproduktion

Personendaten (Adresse, Badges, URL) liegen **nicht im Git**: `private/` ist ignoriert; `card_content.example.json` zeigt das Format (Felder `name`, `company`, `qualification`, `address`, `url`, `badges`).

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
