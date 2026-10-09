# NCRAI Roboter-Visitenkarte – Variante A (EXP)

**Stand:** 2026-10-09 · **Revision:** EXP (experimentell, nicht freigegeben) · **Prozess/Material (Ziel):** MJF, PAC-HP Nylon, Vollfarbe · **Erstmuster:** nicht bestellt

![Vorschau](assets/preview_iso.png)

*(Vorschau: gerendert aus den 3MF-Daten, nicht aus dem CAD. Grauton der Platte = Beleuchtungsschattierung, Material ist weiß.)*

## 1 Kernaussagen

| Aussage | Wert | Einstufung |
|---|---|---|
| Kartendicke geschlossen | **2,4 mm** (Ziel < 4 mm erfüllt) | Entwurf |
| Gedruckte Pose | offen, Steg entspannt bei 55°, Bounding Box 86 × 54 × 37,9 mm | Entwurf |
| Scharnier | Filmscharnier 0,8 mm × 8 mm × 24 mm | **weicht von der PAC-HP-Wandregel (2,0 mm) ab** |
| Randfaserdehnung beim Schließen | 4,8 % | `estimated` (ideale Biegung), Werkstoffgrenze PAC-HP **k.A.** |
| Farbdaten | 3MF mit Texturatlas (3MF Materials Extension), 20 px/mm | Annahme der Lieferantenseite **k.A.** |
| Haltemechanik geschlossen | keine (kein Rastelement) | offener Punkt, Muster entscheidet |

### Warum nicht dünner mit Stiftscharnier?

Rechnung nach den MJF-Regeln (Supplier CN-A, Herstellerdaten, indikativ):

| Variante | Mindest-Gelenkdurchmesser | Kartendicke |
|---|---|---|
| Stiftscharnier, Wand 2,0 mm (PAC-HP) | Stift 2,0 + 2 × Spiel 0,6 + 2 × Wand 2,0 = **7,2 mm** | ≥ 7,2 mm |
| Stiftscharnier, Wand 1,5 mm (Feature-Regel) | **6,2 mm** | ≥ 6,2 mm |
| Zwei gestapelte Paneele à 2,0 mm | – | ≥ 4,0 mm (nicht < 4) |
| **Genestete Karte + Filmscharnier (gewählt)** | – | **2,4 mm** |

Folgerung (Ableitung): Unter 4 mm geht nur eine einlagige Karte, in der das Roboter-Paneel im Fenster der Platte liegt. Das Filmscharnier ist dabei die einzige Gelenkart, die dünn genug ist. Sie verletzt die Wandregel bewusst und ist das Hauptrisiko von Variante A.

## 2 Konzept

| Zustand | Beschreibung |
|---|---|
| Geschlossen (versandfertig) | Roboter-Paneel liegt bündig im Fenster der Platte (Spalt 0,8 mm). Oben QR-Code mit Logo, rechts der flach liegende Roboter. Unterseite: NCRAI-Wortlogo. Kartenmaß 86 × 54 × 2,4 mm. |
| Offen (gedruckte Pose) | Das Paneel steht 55° geneigt auf dem Filmscharnier. Ein Abstützen ist nicht nötig, weil der Steg in dieser Lage spannungsfrei ist. |
| Gedruckt | In der offenen Pose, Platte flach auf dem Bett, ohne Stützen (Pulverbett). Das Schließen biegt den Steg elastisch. |

Rückstellung: Der Steg federt das Paneel beim Loslassen wieder auf. Ein Halteelement fehlt noch (Gummiband, Etui oder Rastnase wären Optionen, `ASSUMPTION`: für das Erstmuster entbehrlich).

## 3 Annahmen und fehlende Information

| ID | Annahme / Lücke | Status |
|---|---|---|
| A1 | Faltung: Roboter klappt als 3D-Figur auf, Variante A = Paneel mit Gelenk | festgelegt |
| A2 | Roboter: neutraler NCRAI-Humanoid, kein Unitree-Design („R3“ ist der Unitree-Handcontroller; Quelle: unitree.com/mobile/R3) | festgelegt |
| A3 | Die hochgeladene Roboter-Karte (2018, Lizenz k.A.) war nur ein Beispiel. Interne Nutzung, nicht im Repo, keine Geometrie übernommen | festgelegt |
| A4 | Farben des ersten Musters: `#2CE9FD` → `#3254A9` → `#4D1DB4` (aus dem Logo gemessen), Navy `#101A3A`. Anpassung nach Erhalt des Erstmusters | festgelegt, `estimated` |
| A5 | Farbübergabe als 3MF mit Textur. Ob der Lieferant die Materials Extension liest, ist **k.A.** (Rückfallformate: OBJ+MTL+PNG, PLY mit Vertexfarben) | im DFM zu klären |
| A6 | URL mit abschließendem „/“, wie vom Nutzer angegeben | festgelegt |
| A7 | Dehnungsgrenze des Filmscharniers 5 % angenommen, Werkstoffdaten PAC-HP **k.A.** | `ASSUMPTION` |
| A8 | Dichte, Masse, Ermüdungsfestigkeit des Scharniers | **k.A.** |

## 4 Parameter (`card_params.py`)

| Parameter | Wert | Einheit | Quelle / Status |
|---|---|---|---|
| `card_w`, `card_h` | 86,0 / 54,0 | mm | Entwurf |
| `t` (Platte, Paneel) | 2,4 | mm | ≥ 2,0 PAC-HP-Wand (Herstellerdaten, indikativ) |
| `gap` Paneel ↔ Fenster | 0,8 | mm | ≥ 0,6 MJF bewegliche Teile (Herstellerdaten) |
| `web_t`, `web_len`, `web_w` | 0,8 / 8,0 / 24,0 | mm | Entwurf, **weicht ab** (Wand 2,0), Detail min. 0,8 erfüllt |
| `relax_deg` | 55 | ° | Entwurf, begrenzt die Dehnung auf 4,8 % |
| `margin` (Plattenrand um Fenster) | 2,6 | mm | berechnet, ≥ 2,0 erfüllt |
| `qr_cx` | −17,0 | mm | Entwurf |
| QR: Version / ECC / Modul / Logoblock | 4 / H / 1,2 mm / 9 × 5 | – | siehe Abschnitt 6 |
| Silhouette | 9 Rechtecke, 28 × 40 mm | mm | eigener Entwurf, Mindeststege 4,0 mm (Arme), Schlitze 1,2 mm |

Toleranz laut Hersteller ±0,3 mm bis 100 mm (indikativ). Spalt 0,8 mm ergibt damit im Worst Case 0,2–1,4 mm (Ableitung, beide Flächen ±0,3 mm). Nach dem Muster ggf. anpassen.

## 5 Geometrieprüfung (2026-10-09, CadQuery 2.8.0, trimesh)

| Prüfung | Ergebnis |
|---|---|
| Solid gültig, Anzahl Körper | gültig, 1 Körper (Platte, Steg und Paneel verschmolzen) |
| STL/3MF wasserdicht | ja |
| STEP-Reimport | gültig, 1 Körper, Volumen 9 662 mm³ |
| Geschlossene Pose | Abstand Paneel ↔ Platte 0,80 mm, keine Überlappung, Paneel bündig 0…2,4 mm |
| Kartendicke geschlossen | 2,4 mm |
| Regelabgleich (`mjf_findings`) | genau 1 Abweichung: Filmscharnier 0,8 mm < 2,0 mm Wand |

Nicht geprüft: Kollision beim Schließvorgang (nur Endlagen), FEM, Ermüdung, Pulverentfernung.

## 6 QR-Code mit Logo

Erzeugt mit `qr_logo.py` (Logo: `assets/ncrai_logo_transparent.png`, Hintergrund transparent).

| Merkmal | Wert |
|---|---|
| Inhalt | `https://nc-robots-ai.com/` |
| Version / Matrix | 4 / 33 × 33, Fehlerkorrektur H |
| Modulgröße | 1,2 mm → Code 39,6 mm, mit Ruhezone 49,2 mm |
| Logo-Aussparung | 9 × 5 Module = 4,1 % → Logo ca. 8,8 × 4,8 mm |
| Farbdruck statt Relief | flächig, Modulkante = Texturkante (24 px je Modul) |
| Prüfung | Dekodierung mit OpenCV (Aruco-Detektor) aus der Rasterdatei **und** aus den gerenderten 3MF-Daten: OK |

Fehlerreserve (eigene Messung, OpenCV, zufällig gekippte Datenmodule, 40 Versuche je Zelle, nur indikativ):

| Aussparung | Fläche | 3 Fehler | 6 Fehler | 10 Fehler |
|---|---|---|---|---|
| 9 × 5 (gewählt) | 4,1 % | 100 % | 100 % | 85 % |
| 11 × 7 | 7,1 % | 97 % | 82 % | 47 % |
| 13 × 7 | 8,4 % | 88 % | 38 % | 10 % |

Ein größeres Logo verbraucht die Fehlerreserve. Lesbarkeit der Logobuchstaben im Druck: **k.A.** Der Praxistest mit mehreren Smartphones am Erstmuster ist Pflicht.

## 7 Farbdaten (3MF)

| Merkmal | Wert |
|---|---|
| Format | 3MF, Materials Extension (`texture2d`, `texture2dgroup`, `requiredextensions="m"`), Filter `nearest` |
| Textur | ein Atlas 1720 × 3020 px (20 px/mm): Plattenoberseite (QR), Plattenrückseite (Wortlogo, gespiegelt vorgezeichnet), Paneelvorderseite (Roboter mit Verlauf, Visier, Brust mit Dome-Symbol), Vollfarbflächen für Kanten und Paneelrückseite |
| Dateigröße | 0,3 MB, 476 Dreiecke |
| Verifikation | Rendering direkt aus den 3MF-Daten (UV-Zuordnung geprüft, QR lesbar) |
| Risiko | Lieferant liest die Extension nicht → Datei wird abgelehnt oder grau gedruckt. Daher `requiredextensions` gesetzt, damit es nicht still passiert |

Farbraum und Wiedergabe des Verlaufs im Vollfarb-MJF-Druck sind **k.A.** und werden am Erstmuster beurteilt.

## 8 Risiken

| Risiko | Wirkung | Maßnahme | Priorität |
|---|---|---|---|
| Filmscharnier bricht oder ermüdet | Karte unbrauchbar | Muster, Scharnier-Coupon (Stegdicke 0,6/0,8/1,0 × Länge 6/8/10 mm) | hoch |
| Steg zu dünn für den Druck (Wand-/Detailregel) | Steg fehlt oder reißt beim Entpulvern | DFM-Rückmeldung, ggf. 1,0 mm | hoch |
| Kein Haltemechanismus | Karte klappt auf | Etui oder Rastnase nach Muster | mittel |
| Textur-3MF wird nicht akzeptiert | keine Vollfarbe | DFM vor Bestellung, Rückfallformate | hoch |
| Pulverreste im Spalt | Klemmen | Reinigungsvermerk im Auftrag | mittel |
| Farbabweichung Logo | Markenwirkung | Erstmuster, Farbwerte nachführen | mittel |

## 9 Vorgehen und Freigaben

| Schritt | Inhalt | Freigabe |
|---|---|---|
| 1 | Erstmuster-Anfrage (DFM) mit STEP + 3MF | **ja** (Upload, Kontakt, Kosten k.A.) |
| 2 | Optional vorher: Coupon für Filmscharniere (neue Übung) | nein |
| 3 | Farb- und Scharnier-Anpassung nach Erstmuster (neue Revision) | nein |
| 4 | Veröffentlichung im öffentlichen Repo (Logo, QR, Dateien) | **ja** |

## 10 Dateien und Neuerzeugung

| Datei | Zweck |
|---|---|
| `card_params.py` | Parameter, Validierung, Regelabgleich |
| `robot_card.py` | CadQuery-Quelle: Plate + Fenster, Filmscharnier (Bogen), Paneel |
| `qr_logo.py` | QR-Code mit Logo |
| `card_colour.py` | Texturatlas, UVs, 3MF, Software-Rendering zur Prüfung |
| `assets/` | Logo (transparent), QR (SVG in mm, PNG, CSV), Vorschauen |
| `exports/step/NCRAI-card_variant-A_EXP_MJF_PAC-HP_2026-10-09.step` | Geometrie (ohne Farbe), abgeleitet |
| `exports/3mf/NCRAI-card_variant-A_EXP_MJF_PAC-HP_2026-10-09.3mf` | Geometrie + Farbe, abgeleitet |

```bash
python cad/functional-prototypes/ncrai-robot-card/robot_card.py --out <dir> --date 2026-10-09
python cad/functional-prototypes/ncrai-robot-card/card_colour.py --stl <dir>/NCRAI-card_variant-A_EXP_MJF_PAC-HP_2026-10-09.stl --out <dir>
ruff format . && ruff check . && pytest -q
python scripts/validate_cad_exports.py && python scripts/generate_manifest.py
```

## 11 Quellen

| Quelle | Inhalt | Stand |
|---|---|---|
| Supplier CN-A (anonymisiert), `docs/reference/supplier-cn-a/design-guidelines.md` und CSV unter `data/material-datasheets/supplier-cn-a/` | Spalt, Wand, Detail, Pin, Toleranz, PAC-HP | Erhebung 2025-11-02 / Repo-Stand 2026-10-08, vor RFQ neu prüfen |
| Unitree Robotics, https://www.unitree.com/mobile/R3 | R3 = Controller | abgerufen 2026-10-09 |
| ISO/IEC 18004 (QR-Code, Fehlerkorrektur, Ruhezone) | Aufbau, Stufe H | nicht im Volltext eingesehen |
| 3MF Consortium, Materials and Properties Extension | Texturen in 3MF | nicht im Volltext eingesehen, Umsetzung nach Standardbeschreibung |
| Eigene Messungen | Beispieldatei-Analyse, QR-Decodertests, Geometrieprüfung | 2026-10-09 |
