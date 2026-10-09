# NCFAI-Visitenkarte – 3D-gedrucktes Unikat (EXP)

**Stand:** 2026-10-09 · **Revision:** EXP (nicht freigegeben) · **Prozess/Material:** MJF, PAC-HP Nylon (Vollfarbe), Supplier CN-A

## 1 Anforderungen → Umsetzung

| Anforderung | Umsetzung |
|---|---|
| 85 × 55 mm | exakt 85 × 55 mm, Ecken R4 |
| Dicke max. 2,5 mm | **2,2 mm nominal**: 2,2 + 0,3 (Toleranz) = 2,5; 2,2 ≥ 2,0 (Wandminimum PAC-HP). Fenster 2,0–2,2 mm (`card_params.py` erzwingt es) |
| Farbmaterial, Logo gut sichtbar | PAC-HP Nylon (MJF, Vollfarbe, Herstellerdaten Supplier CN-A). Weißer Grund = höchster Kontrast für den Logo-Verlauf |
| wenig Verzug | gleichmäßige Dicke, symmetrischer Querschnitt (kein Relief/keine Rippen), Ecken R4, Löcher ≥ 4 mm vom Rand, Kontrollvariante ohne Löcher (`--bubbles 0`) |
| Unikat | Seed-basiert: Lage/Größe der durchgehenden „Bierbläschen“-Löcher (Vorderseite, 7 Stk.), Bläschen-Muster und Kennung `No. <Hash>` auf der Rückseite. Gleicher Seed = identische Karte |

## 2 Geometrie-Entscheidung (Verzug)

| Option | Bewertung |
|---|---|
| Ebene Platte, gleichmäßig 2,2 mm, R4 | **gewählt** – erfüllt Wand ≥ 2,0 und ≤ 2,5 gesamt |
| Erhabene Rahmenrippe / Prägung | verworfen: Prägung min. 0,8 mm (konservativ) + Wand 2,0 > 2,5 mm gesamt |
| Wabe / Gitterkern | verworfen: Wandminimum 2,0 mm |
| Gewölbte Karte | verworfen: nicht stapelbar, Bauhöhe > 2,5 mm |
| Perforation (Bläschen) | Teil des Unikats; Verzugswirkung **k.A.** → Vergleich über EX-001 |

Verzugsursachen/Hebel (Literatur-/Erfahrungswissen, **nicht gemessen**): ungleichmäßige Abkühlung, ungleiche Wandstärke, scharfe Ecken, einseitige Masseverteilung. Ausrichtung im Bauraum entscheidet der Dienstleister (Änderung nur mit schriftlicher Freigabe, siehe CLAUDE.md).

## 3 Annahmen / offen

| Punkt | Status |
|---|---|
| Firmenkürzel | Vorgabe „NCAI“ → `ASSUMPTION` Tippfehler, verwendet wird **NCFAI** (Logo) |
| „Biersommeliere“ | `ASSUMPTION` Tippfehler → „Biersommelier“ gedruckt; vor Bestellung bestätigen |
| Schriftgröße min. 2,6 mm (Strich ≈ 0,4 mm) | `ASSUMPTION`, Farbauflösung PAC-HP `k.A.` |
| Farbtreue | sRGB-Quelle ≠ Prozessfarbe (Anbieter warnt vor Abweichung); Orange/Blau-Verlauf `k.A.` → Erstmuster |
| Dateiformat | OBJ + MTL + 2 PNG (ZIP) enthält die Verläufe als Textur; ob PAC-HP Texturen liest, ist laut Herstellerseite nur für „Full-Color-Resin“ ausdrücklich dokumentiert (OBJ+MTL+PNG), für PAC-HP „OBJ oder 3MF“ → **vor Bestellung beim Support klären** |
| Farbe nur einseitig/ungleich verteilt | Einfluss auf Verzug `k.A.` |
| Gewicht ≈ 10 g | `estimated` (10 094 mm³ × ≈ 1,0 g/cm³, Dichte `ASSUMPTION`) |
| STEP-Master | wird erzeugt, sobald `cadquery` installiert ist (Umgebung: nicht verfügbar → **offen**) |

## 4 Reproduktion

Personendaten (Adresse) liegen **nicht im Git**: `private/` ist ignoriert; `card_content.example.json` zeigt das Format.

```bash
pip install numpy pillow shapely mapbox-earcut trimesh networkx lxml   # optional: cadquery
python cad/functional-prototypes/ncfai-business-card/ncfai_card.py \
  --content private/ncfai-business-card/card_content.json \
  --logo private/ncfai-business-card/ncfai_logo.png \
  --out private/ncfai-business-card --date 2026-10-09 [--seed TEXT] [--bubbles 0]
```

## 5 Prüfungen (2026-10-09)

| Prüfung | Ergebnis |
|---|---|
| STL wasserdicht, 1 Schale, Maße 85,00 × 55,00 × 2,20 | bestanden |
| kleinster Steg Loch–Loch/Rand ≥ 2,0 mm | 2,58 mm |
| kleinstes Loch ≥ 1,5 mm + Toleranz | Ø 2,7 mm |
| `supplier_dfm_check.py MJF` Wand/Loch | bestanden (Gesamt-Freigabe ersetzt das nicht) |
| Mindest-Detail 0,8 mm | gilt für Relief/Gravur; hier keine – Farbdruck flach |
| Slicer-/Anbieter-Vorschau, Farbmuster, Ebenheit | **offen** (EX-001) |

Keine Bestellung, kein Upload, keine Anfrage ohne ausdrückliche Freigabe.
