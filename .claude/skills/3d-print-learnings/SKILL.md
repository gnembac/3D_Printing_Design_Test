---
name: 3d-print-learnings
description: Erfahrungswissen aus dem Projekt 3D_Printing_Design_Test für Teile, die extern in MJF PAC-HP Vollfarbe (JLC3DP / Supplier CN-A) gefertigt werden: dünne Visitenkarten und Scharniere, Farb-3MF (Textur, lib3mf-Prüfung), QR-Code mit Logo, Regelabgleich, CadQuery-Prüfroutinen und Repo-Fallstricke. IMMER verwenden bei Konstruktion, Farbexport, Bestellvorbereitung oder Review von Karten, Scharnieren, QR-Codes, 3MF/STEP-Exporten für Druckdienste, oder wenn ein neues Teil für MJF/PAC-HP, Filmscharnier, Print-in-Place oder Vollfarbdruck entworfen wird.
---

# 3D-Druck: gelernte Regeln und Prüfroutinen

**Stand:** 2026-10-09 · Quelle: Sitzung NCRAI-Roboterkarte (PR gnembac/3D_Printing_Design_Test#6) und Projekt-`CLAUDE.md`.
`CLAUDE.md` bleibt maßgeblich. Alle Hersteller-/Dienstwerte sind **Herstellerdaten, indikativ** (Supplier CN-A bzw. JLC3DP-Hilfeseiten, Seiten 1–3 Jahre alt) und vor jeder Bestellung neu zu prüfen. Nicht belegte Werte `k.A.`, Annahmen `ASSUMPTION`, Ableitungen `estimated`.

## 1 Vorgehen (Reihenfolge)

1. Nutzerangaben prüfen, bevor gebaut wird (Beispiel: „Unitree R3“ ist der **Handcontroller**, kein Humanoid; Hochgeladene Fremddateien: Lizenz klären, nicht ins Repo).
2. Fehlende Information und Ziele per Rückfrage klären (Faltkonzept, Dicke, Referenz, Lizenz), danach bauen.
3. Parametrisches Modell mit reinem Parametermodul (`*_params.py`, testbar, ohne CAD-Abhängigkeit) und getrenntem CadQuery-Builder.
4. Regelabgleich (`scripts/supplier_dfm_check.py MJF --max-dim … --wall … --detail … --clearance-moving …`) und `mjf_findings()` im Parametermodul.
5. Geometrie prüfen (Abschnitt 6), Export, `validate_cad_exports.py`, `generate_manifest.py`.
6. Ruff, Pytest, `check_repo_hygiene.py`. Erst dann committen, **nur auf ausdrückliche Freigabe** (Stop-Hook-Meldungen ersetzen sie nicht).

## 2 MJF / PAC-HP: Regelwerte (Supplier CN-A, indikativ)

| Größe | Wert | Anmerkung |
|---|---|---|
| Wandstärke PAC-HP | ≥ 2,0 mm | MJF allgemein 1,0–2,0 je Teilegröße |
| Feature-Wand (Bosse, Rastnasen) | ≥ 1,5 mm | |
| Detail (Relief, Gravur) | ≥ 0,8 mm | MJF-Artikel nennt 0,5, konservativer Wert gilt |
| Spalt bewegliche Teile | ≥ 0,6 mm | Montagespalt 0,2–0,4 mm |
| Stift | Ø ≥ 2,0 mm, Höhe/Ø ≤ 2 | |
| Toleranz | ±0,3 mm bis 100 mm | Spalt 0,8 mm → real 0,2–1,4 mm (Worst Case) |
| Bauraum PAC-HP | 190×223×248 oder 320×175×225 mm | Quelle widersprüchlich |

Nicht verwenden: Werte mit `quality_flag` `implausible`, `suspect_copy`, `not_traceable`. Bei Konflikten gilt der konservative Wert.

## 2a Auftragsprüfung des Dienstes (JLC3DP, 2026-10-09, aus echter Rückmeldung)

| Prüfung | Wert | Folge |
|---|---|---|
| Wandstärke | warnt unter 1,0 mm, ideal 2,0 mm; markiert die dünne Stelle rot mit Maß (Film-Steg 0,80 mm) | Steg mindestens 1,0 mm plus Reserve (1,1 mm), nie genau auf dem Grenzwert auslegen |
| Text/Prägung/Gravur | Nylon und Resin ≥ 0,8 mm, Metall und Kunststoff ≥ 1,0 mm (Breite **und** Tiefe) | Schlitze und Spalte (auch Spielspalte) ≥ 1,0 mm planen; Reserve gegen Netz-Tessellierung |
| Mehrteilige Aufträge | die Warnung nennt Maße je Teil (hier 0,56 / 0,60 / 0,80); Screenshot-Maße dem richtigen Teil zuordnen, bevor man ändert | |
| Idealwert 2,0 mm | mit Filmscharnier unvereinbar (ε = h·θ/(2L) > 5 % schon bei ca. 23°); Dienstminimum 1,0 mm anstreben und das Muster entscheiden lassen | |

Varianten behalten und mit Preset benennen (`--variant a1|a2`), beanstandete Dateien als überholt markieren, nicht überschreiben.

## 3 Dünne Karten und Scharniere

| Erkenntnis | Wert / Formel |
|---|---|
| Print-in-Place-Stiftscharnier, Mindest-Ø | Stift + 2 × Spiel + 2 × Wand = 2,0 + 1,2 + 2 × 2,0 = **7,2 mm** (mit Feature-Wand 1,5: 6,2 mm) |
| Zwei gestapelte Paneele à 2,0 mm | ≥ 4,0 mm, also nie unter 4 mm |
| Unter 4 mm | **einlagig genestet**: Paneel liegt im Fenster der Platte (Spalt 0,8 mm), Filmscharnier als Gelenk (Karte 2,4 mm) |
| Randfaserdehnung Filmscharnier | ε ≈ h · θ / (2 · L) (h Stegdicke, θ Winkel in rad, L freie Länge). Beispiel 0,8 mm, 55°, 8 mm → 4,8 % |
| Dehnungsgrenze PAC-HP | **k.A.**; Annahme 5 % (`ASSUMPTION`), Muster entscheidet |
| Druckpose | Teil in entspannter (offener) Pose drucken, Schließen biegt den Steg; Steg 0,8 mm verletzt die Wandregel bewusst, im Regelabgleich als einzige Abweichung ausweisen |
| Haltemechanik geschlossen | fehlt noch, Steg federt auf (Rastnase/Etui nach Muster) |

## 4 Farbdaten für JLC3DP (PAC-HP Vollfarbe)

| Punkt | Regel |
|---|---|
| Format | **3MF mit allen Farbdaten**, sonst Fertigung grau; eine Schale je Datei (mehrere Schalen wurden abgelehnt) |
| Textur-3MF | 3MF Materials Extension: `m:texture2d` + `m:texture2dgroup`, `requiredextensions="m"`, Filter `nearest`, **ein gemeinsamer Atlas** (zwei Texturen: manche Viewer zeigen dann die Vorderseite auch hinten) |
| Beziehungstyp | `http://schemas.microsoft.com/3dmanufacturing/2013/01/3dtexture` in `3D/_rels/3dmodel.model.rels`, nicht `…/3dmodeltexture` (sonst lib3mf „Invalid texture“) |
| Prüfung | **lib3mf strikt** lesen: 0 Warnungen, Textur- und Gruppenzahl stimmen; zusätzlich Software-Rendering aus den 3MF-Daten (UV-Zuordnung, QR-Dekodierung) |
| Ausweichformate | Farbe je Vertex (`colorgroup`, Netz fein, ca. 20 MB, siehe `ncfai-business-card/export_3mf.py`), OBJ+MTL+PNG, PLY |
| Falscher Weg | Netz am Raster zerschneiden, um Dreiecksfarben zu bekommen: Millionen Dreiecke (161 MB), unbrauchbar. Teilweises Unterteilen erzeugt T-Kreuzungen (nicht wasserdicht). Texturen sind der richtige Weg |
| Unbekannt (k.A.) | ob der Dienst die Textur liest. Vorschau der Angebotsseite auf Farbe prüfen, bei Grau nicht bestellen, Support fragen |
| Farbwiedergabe | Farbraum und Verlauf im MJF-Druck k.A., am Erstmuster beurteilen; Logofarben Cyan `#2CE9FD`, Mitte `#3254A9`, Violett `#4D1DB4` (aus Logo gemessen, `estimated`) |

## 5 QR-Code mit Logo

| Erkenntnis | Wert |
|---|---|
| Fehlerkorrektur | H; URL `https://nc-robots-ai.com/` (25 Zeichen) → Version 4, 33×33 Module; ohne Schrägstrich am Ende Version 3-H |
| Logo-Aussparung | **≤ 5 % der Codefläche** (9×5 Module = 4,1 %). Gemessen: 9×5 hält 6 Fehler zu 100 %, 13×7 (8,4 %) nur 38 % |
| Modulgröße | ≥ 0,8 mm (Detailregel), gewählt 1,2 mm → 49,2 mm inkl. Ruhezone 4 Module |
| Farbdruck statt Relief | Modulkante = Texturkante, Kontrast Navy auf Weiß |
| Decoder | OpenCV: `QRCodeDetectorAruco`. Der klassische `QRCodeDetector` liest selbst saubere Referenzcodes nicht |
| Prüfen | aus der Rasterdatei **und** aus den gerenderten 3MF-Daten dekodieren; echte Smartphone-Prüfung am Muster ist Pflicht |

## 6 Geometrieprüfung (immer vor dem Export)

| Prüfung | Werkzeug |
|---|---|
| Solid gültig, Anzahl Körper | CadQuery `isValid()`, `Solids()` |
| Spalt und Überlappung | `Shape.distance()`, `intersect().Volume()`; geschlossene Pose als Gegenprobe nachbauen |
| STL/3MF wasserdicht, Schalen | trimesh `is_watertight`, `split()` |
| STEP-Reimport | `cq.importers.importStep`, Volumen vergleichen |
| Dateianalyse fremder Dateien | trimesh + scipy (`cKDTree`) für Spalte zwischen Körpern; `shapely` nicht voraussetzen |
| Umgebung | venv im Scratchpad; `cadquery`, `trimesh`, `qrcode`, `pillow`, `opencv-python-headless`, `lib3mf` |

## 7 Repo-Fallstricke

- **Modulnamen** in `cad/functional-prototypes/*` global eindeutig halten (`ncrai_card_params`, nicht `card_params`): Tests importieren per `sys.path`, gleiche Namen kollidieren.
- **Übungs-IDs** vor der Vergabe in `exercises/` und auf `main` prüfen (EX-001 war doppelt, Scharnier-Coupon wurde EX-002).
- **Merge statt Rebase**; Konflikt in `requirements-dev.txt`: alle Abhängigkeiten behalten, jede Bibliothek nur **einmal** (pip lehnt doppelte Einträge ab).
- Ruff-Zeilenlänge 100; `ruff format .` vor dem Commit.
- Manifest nach jedem Export neu erzeugen (`generate_manifest.py`).
- Lieferantenname: in `docs/suppliers/` anonymisieren; Klartext nur auf ausdrücklichen Wunsch und vor Veröffentlichung neu entscheiden. Kein Preis, keine Kontaktdaten, kein Upload, keine Bestellung ohne Freigabe.
- Persönliche Daten (Name, Adresse) nicht ins öffentliche Repo.
- Sandbox: `pkill` und `rm -rf` können gesperrt sein, Hintergrundjobs mit `TaskStop` beenden; neue Ausgabeordner statt Löschen.

## 8 Offene Lernfragen (zuerst am Erstmuster klären)

| Frage | Messung |
|---|---|
| Filmscharnier 0,8 mm: Bruch, Ermüdung, Entpulverung | Zyklen bis Anriss, Stegdicke, Spalt (Fühlerlehre) |
| Liest JLC3DP die Textur-Farbe | Vorschau der Angebotsseite, Supportantwort |
| Farbtreue Verlauf, Lesbarkeit der Logobuchstaben im QR | Foto bei Tageslicht, 3 Smartphones, 2 Lichtlagen |
| Übertragbarkeit FDM-Coupon (EX-002) auf MJF | MJF-Muster des Coupons (nur mit Freigabe) |
