# Projekt: Wissenschaftlich fundierte 3D-Druck-Experimente

> **Hinweis:** Dies ist das ursprüngliche, ausführliche deutsche
> Spezifikationsdokument dieses Projekts. Für die tägliche Arbeit mit
> Claude Code ist [`.claude/CLAUDE.md`](../../.claude/CLAUDE.md) die
> maßgebliche, aktiv geladene Anweisung (auf Englisch, um Lernprojekt- und
> GitHub-Konventionen zu ergänzen). Bei Widersprüchen gilt `CLAUDE.md`.
> Dieses Dokument bleibt als ausführliche fachliche Wissensbasis erhalten.

## 1. Rolle und Zielsetzung

Du agierst als interdisziplinärer Entwicklungsassistent für:

- Additive Fertigung / 3D-Druck  
- Konstruktion und DfAM (Design for Additive Manufacturing)  
- Polymer-, Metall- und Verbundwerkstoffe  
- Materialwissenschaft und Werkstoffprüfung  
- Statistische Versuchsplanung (DoE)  
- Datenanalyse, Qualitätsmanagement und Kostenoptimierung  
- Technische Dokumentation für Fertigungspartner in Europa und China

Das Ziel ist nicht nur das Erzeugen von STL-Dateien. Entwickle einen reproduzierbaren, datenbasierten Experimentierprozess, mit dem die Zusammenhänge zwischen:

1. Bauteilgeometrie,  
2. Druckverfahren,  
3. Material,  
4. Druckparametern,  
5. Orientierung im Bauraum,  
6. Nachbearbeitung,  
7. Kosten,  
8. Maßhaltigkeit,  
9. mechanischen Eigenschaften,  
10. Alterung und Umwelteinfluss

systematisch untersucht und optimiert werden.

Das Projekt soll sowohl für eigene Desktop-Drucker als auch für externe Fertigung in Europa und China geeignet sein.

---

## 2. Grundprinzipien

### 2.1 Wissenschaftliche Arbeitsweise

Arbeite nach folgenden Prinzipien:

- Formuliere vor jedem Experiment eine klare Hypothese.  
- Definiere unabhängige Variablen, abhängige Variablen und Störgrößen.  
- Verwende geeignete DoE-Verfahren anstelle unsystematischer Einzeltests.  
- Wiederhole kritische Messungen.  
- Dokumentiere Unsicherheiten, Messmittel, Kalibrierung und Umgebungsbedingungen.  
- Trenne Herstellerdaten, Literaturwerte und eigene Messergebnisse eindeutig.  
- Kennzeichne fehlende Informationen mit `k.A.`.  
- Kennzeichne abgeleitete oder nicht direkt gemessene Werte mit `geschätzt`.  
- Nenne verwendete Quellen, Normen, Datenblätter und Studien.  
- Keine Material- oder Festigkeitsbehauptung ohne Angabe von Prüfbedingung, Norm, Probenorientierung und Herstellverfahren.

### 2.2 Wichtige Einschränkung

Mechanische Kennwerte von 3D-Druckteilen sind nicht identisch mit Kennwerten von Spritzgussteilen oder Halbzeugen.

Berücksichtige insbesondere:

- Anisotropie durch Schichtaufbau  
- Haftung zwischen Schichten  
- Porosität und Lufteinschlüsse  
- Feuchteaufnahme des Filaments oder Pulvers  
- Kristallinität und Abkühlgeschwindigkeit  
- Faserorientierung bei fasergefüllten Werkstoffen  
- Druckrichtung und Bauteilorientierung  
- Düsendurchmesser und Layerhöhe  
- Alterung durch UV, Temperatur, Feuchte und Chemikalien  
- Nachbearbeitung wie Tempern, Annealing, Dampfglätten oder Beschichten

Materialkennwerte aus Datenblättern dürfen nur als Ausgangshypothese verwendet werden. Für belastete Bauteile müssen eigene Prüfkörper und eigene Messungen vorgesehen werden.

---

## 3. Unterstützte Fertigungsverfahren

Berücksichtige mindestens die folgenden Verfahren:

| Verfahren | Typische Materialien | Priorität | Typische Stärken | Kritische Risiken |  
|---|---|---:|---|---|  
| FDM/FFF | PLA, PETG, ABS, ASA, PA, PC, TPU, PP, CF/GF-Filamente | hoch | kostengünstig, schnell iterierbar, große Auswahl | Anisotropie, Verzug, Feuchte, Layerhaftung |  
| SLA/MSLA/DLP | Standard Resin, Tough Resin, Flexible Resin, High Temp Resin | mittel | hohe Detailauflösung, glatte Oberfläche | Sprödigkeit, UV-Alterung, Nachhärtung |  
| SLS | PA12, PA11, TPU | mittel | keine Stützstrukturen, robuste Funktionsbauteile | Rauheit, Pulvermanagement, Maßabweichungen |  
| MJF | PA12, PA11, TPU | mittel | Serienfähigkeit, gute Isotropie im Vergleich zu FDM | externe Fertigung, Mindestmengen |  
| DMLS/SLM | Aluminium, Edelstahl, Titan, Werkzeugstahl | optional | hochfeste Metallteile, komplexe Geometrien | Kosten, Nacharbeit, Eigenspannungen |  
| Binder Jetting | Metalle, Sand, Keramik | optional | Skalierbarkeit, komplexe Bauteile | Dichte, Sintern, Toleranzrisiken |

Für Einsteigerexperimente hat FDM/FFF Priorität. PLA, PETG, ASA und PA sollen als zentrale Vergleichsmaterialien betrachtet werden.

---

## 4. Projektstruktur

Lege folgende Verzeichnisstruktur an:

```text  
3d-print-experiments/  
├── README.md  
├── LICENSE  
├── docs/  
│   ├── project-charter.md  
│   ├── literature-review.md  
│   ├── standards-and-test-methods.md  
│   ├── material-selection-matrix.md  
│   ├── manufacturing-guidelines-eu-china.md  
│   ├── risk-register.md  
│   ├── experimental-protocols/  
│   └── reports/  
├── cad/  
│   ├── parametric/  
│   ├── test-specimens/  
│   ├── functional-prototypes/  
│   └── assemblies/  
├── exports/  
│   ├── step/  
│   ├── stl/  
│   ├── 3mf/  
│   └── drawings/  
├── slicer-profiles/  
│   ├── fdm/  
│   ├── sla/  
│   └── external-manufacturing/  
├── experiments/  
│   ├── DOE-001-printer-calibration/  
│   ├── DOE-002-dimensional-accuracy/  
│   ├── DOE-003-warping-and-shrinkage/  
│   ├── DOE-004-tensile-strength/  
│   ├── DOE-005-compression-strength/  
│   ├── DOE-006-layer-adhesion/  
│   ├── DOE-007-fatigue-and-creep/  
│   ├── DOE-008-environmental-aging/  
│   └── DOE-009-cost-model/  
├── data/  
│   ├── raw/  
│   ├── processed/  
│   ├── material-datasheets/  
│   ├── measurements/  
│   └── results/  
├── scripts/  
│   ├── generate_cad.py  
│   ├── generate_doe.py  
│   ├── analyze_results.py  
│   ├── cost_model.py  
│   ├── material_database.py  
│   └── export_manufacturing_package.py  
├── notebooks/  
├── bom/  
├── quality/  
│   ├── inspection-plans/  
│   ├── calibration/  
│   └── nonconformities/  
└── templates/  
    ├── experiment-protocol-template.md  
    ├── test-report-template.md  
    ├── supplier-rfq-template.md  
    └── part-design-review-template.md  
```

---

## 5. Dateiformate und Lieferpaket

### 5.1 Primäre CAD-Formate

Erzeuge und versioniere Konstruktionen bevorzugt als:

| Zweck | Format | Anforderung |  
|---|---|---|  
| Parametrische Quelle | FreeCAD, CadQuery, OpenSCAD oder STEP-Quellmodell | Pflicht |  
| Austauschformat CAD | STEP AP214 oder AP242 | Pflicht für technische Teile |  
| Druckdatei | 3MF | bevorzugt |  
| Kompatibilitätsformat | STL, binär | zusätzlich |  
| Baugruppenbeschreibung | STEP oder native Baugruppe | bei Baugruppen |  
| Zeichnung | PDF und DXF/DWG, falls erforderlich | bei externen Lieferanten |  
| Druckprofil | 3MF-Projekt oder slicerspezifisches Profil | Pflicht bei eigenen Versuchen |

STL darf nicht das alleinige Masterformat sein, da STL keine Parametrik, Materialdefinition, Maße, Toleranzen oder Baugruppenbeziehungen transportiert.

### 5.2 Anforderungen an STL/3MF

Vor Export validieren:

- Geschlossenes, wasserdichtes Volumen (manifold).  
- Keine selbstschneidenden Flächen.  
- Keine invertierten Normalen.  
- Keine Nullflächen oder degenerierten Dreiecke.  
- Keine offenen Kanten.  
- Einheit Millimeter.  
- Angemessene Tessellierung ohne unnötig große Dateien.  
- Bauteilorientierung dokumentieren.  
- Bauteil-ID, Revision und Material im Dateinamen führen.

Dateinamensschema:

```text  
[projekt]_[teilnummer]_[revision]_[verfahren]_[material]_[datum].3mf  
[projekt]_[teilnummer]_[revision]_[verfahren]_[material]_[datum].stl  
```

Beispiel:

```text  
DOE003_warping_coupon_R02_FDM_ASA_2026-10-04.3mf  
```

---

## 6. Parametrische CAD-Strategie

Erstelle sämtliche Versuchsteile parametrisch. Verwende vorzugsweise:

1. CadQuery oder FreeCAD für technische 3D-Modelle.  
2. OpenSCAD für einfache, transparent parametrisierte Geometrien.  
3. Python-Skripte für Variantenbildung, Dateiexport und DoE-Verknüpfung.

Jedes parametrische Modell benötigt:

- Beschreibung des Verwendungszwecks  
- Liste aller Parameter  
- Einheit jedes Parameters  
- Standardwerte  
- zulässige Wertebereiche  
- Abhängigkeiten zwischen Parametern  
- Validierungsregeln  
- Exportfunktion für STEP und STL/3MF  
- eindeutige Modellrevision  
- Prüfroutine für minimale Wandstärken, Bohrungen, Überhänge und Kollisionsfreiheit

### 6.1 Zentrale CAD-Parameter

Modellparameter sollen mindestens umfassen:

```yaml  
part_id: DOE-003-WARP-COUPON  
revision: R01  
manufacturing_process: FDM  
material: ASA  
nozzle_diameter_mm: 0.4  
line_width_mm: 0.45  
layer_height_mm: 0.20  
wall_count: 4  
wall_thickness_mm: 1.8  
top_bottom_thickness_mm: 1.2  
infill_percent: 30  
infill_pattern: gyroid  
print_orientation: XY-flat  
build_plate_temperature_c: 105  
nozzle_temperature_c: 255  
chamber_temperature_c: k.A.  
shrinkage_compensation_xy_percent: 0.0  
shrinkage_compensation_z_percent: 0.0  
target_tolerance_mm: 0.20  
```

---

## 7. Konstruktionsregeln für FDM/FFF

### 7.1 Wandstärken

Verwende nicht pauschal eine feste Wandstärke. Leite Wandstärken aus Düsendurchmesser, Linienbreite, Belastung, Nachbearbeitung und Material ab.

Als erste konstruktive Orientierung für eine 0,4-mm-Düse:

| Anwendung | Startwert Wandstärke | Typische Perimeter bei 0,45 mm Linienbreite | Hinweis |  
|---|---:|---:|---|  
| Optisches Modell | 0,8–1,2 mm | 2–3 | nur bei geringer Belastung |  
| Allgemeines Gebrauchsteil | 1,2–2,0 mm | 3–4 | bevorzugter Ausgangsbereich |  
| Mechanisch belastetes Teil | 2,0–3,0 mm | 4–6 | Übergänge verrunden |  
| Verschraubung / Lageraufnahme | 3,0 mm oder mehr | abhängig von Last | lokale Verstärkungen nutzen |  
| Druck- oder wasserdichtes Teil | mindestens 1,6–2,4 mm | 4–5 | Perimeter wichtiger als Infill |  
| Flexible TPU-Struktur | mindestens 1,5 mm | abhängig von Shore-Härte | Knicken und Quetschen prüfen |

Diese Werte sind Konstruktionsstartwerte, keine garantiert erreichbaren Kennwerte. Die Mindestwandstärke sollte im Regelfall mindestens dem Zwei- bis Dreifachen der Extrusionsbreite entsprechen; für funktionale Bauteile sind mehrere geschlossene Perimeter wichtiger als ein hoher Infill-Anteil. [4][10]

### 7.2 Geometrie- und DfAM-Regeln

Berücksichtige:

- Vermeide abrupte Wandstärkenwechsel.  
- Verwende Radien statt scharfer Innenecken.  
- Verwende Rippen statt massiver Materialblöcke.  
- Gestalte Rippen typischerweise mit etwa 40–60 % der angrenzenden Wanddicke als Startwert; validiere dies experimentell.  
- Nutze Fasen oder Radien an der ersten Schicht gegen Elephant Foot.  
- Berücksichtige Bohrungsuntermaß, insbesondere bei FDM.  
- Plane bei Passungen Testreihen mit abgestuften Toleranzen.  
- Vermeide große, flache, geschlossene Geometrien bei stark schrumpfenden Materialien.  
- Platziere kritische Belastungsrichtungen möglichst in XY-Ebene, wenn Layerhaftung begrenzend ist.  
- Verwende Heat-Set-Inserts, Mutternfallen, Durchgangsbolzen oder Buchsen statt direkt belasteter Kunststoffgewinde.  
- Plane für Schraubverbindungen ausreichende Randabstände und lokale Wandverstärkung.  
- Verwende Dichtflächen mit ausreichender Breite, mehreren Perimetern und möglichst wenig Top-/Bottom-Übergängen.  
- Hohle dicke Bauteile aus, wenn keine Masse oder Vollmaterialsteifigkeit erforderlich ist.

Ungleichmäßige Abkühlung erzeugt thermische Spannungen und Verzug. Große flache Geometrien, starke Querschnittssprünge und ungeeignete Bauraumorientierung sind daher besonders kritisch. [10][12]

---

## 8. Materialdaten und Materialwissenschaft

### 8.1 Zu erfassende Materialeigenschaften

Für jedes Material ist ein strukturiertes Datenblatt anzulegen:

| Kategorie | Kennwerte |  
|---|---|  
| Allgemein | Hersteller, Produktname, Charge, Farbe, Durchmesser, Trocknungszustand |  
| Thermisch | Glasübergangstemperatur Tg, Schmelztemperatur Tm, HDT, Vicat, empfohlene Drucktemperatur |  
| Mechanisch | Zugfestigkeit, Streckgrenze, Bruchdehnung, E-Modul, Biegefestigkeit, Biegemodul, Schlagzähigkeit, Druckfestigkeit |  
| Zeitabhängig | Kriechen, Relaxation, Ermüdung, Alterung |  
| Physikalisch | Dichte, Feuchteaufnahme, Wärmeausdehnungskoeffizient, Wärmeleitfähigkeit |  
| Chemisch | Beständigkeit gegen Wasser, Öl, Kraftstoff, Säuren, Laugen, Alkohol, UV |  
| Druckbarkeit | Verzug, Haftung, Stringing, Bridging, Schichthaftung, Geruch, Emissionen |  
| Mikrostruktur | amorph, teilkristallin, kristallin; Füllstoffe; Fasern; Polymermorphologie |  
| Wirtschaftlich | Filamentpreis, Ausschussrate, Druckzeit, Energiebedarf, Nacharbeitsaufwand |

### 8.2 Materialklassen

Vergleiche mindestens:

| Material | Morphologie | Typische Eignung | Wesentliche Risiken |  
|---|---|---|---|  
| PLA | überwiegend amorph bis teilkristallin, abhängig von Type und Annealing | Prototypen, Maßhaltigkeit, steife Teile | Wärmebeständigkeit, Sprödigkeit, Hydrolyse bei ungünstiger Lagerung |  
| PETG | überwiegend amorph | robuste Allround-Teile, Behälter, Halterungen | Stringing, Kriechen, geringere Steifigkeit als PLA |  
| ABS | amorph | technische Innenraumteile | Verzug, Emissionen, UV-Alterung |  
| ASA | amorph | Außenanwendungen, UV-beständige Teile | Verzug, Einhausung sinnvoll |  
| PA6 / PA12 | PA6 teilkristallin; PA12 teilkristallin | zähe Funktionsbauteile, Clips, Lagerumgebung | Feuchteaufnahme, Schrumpfung, Trocknungsbedarf |  
| PC | amorph | hochsteife und wärmebeständige Teile | hohe Drucktemperatur, Rissbildung, Feuchte |  
| TPU | segmentiertes Elastomer | Dämpfung, flexible Teile, Dichtungen | dimensionskritische Geometrien, Druckgeschwindigkeit |  
| PP | teilkristallin | Chemikalienbeständigkeit, Scharniere | starke Schrumpfung, Haftung auf Druckbett |  
| CF-/GF-gefüllte Polymere | Polymermatrix mit Kurzfasern | Steifigkeit, Wärmeformstabilität | Abrasion, Richtungsabhängigkeit, Bruchdehnung reduziert |

Begriffe wie Zugfestigkeit, E-Modul und Bruchdehnung müssen immer getrennt bewertet werden: Zugfestigkeit beschreibt den Widerstand gegen Bruch unter Zug; ein hoher E-Modul steht für hohe Steifigkeit, jedoch nicht automatisch für hohe Schlagzähigkeit oder Duktilität. [2]

### 8.3 Normen und Prüfmethoden

Verwende, sofern möglich, folgende Normen als Referenz:

| Eigenschaft | Bevorzugte Norm / Methode |  
|---|---|  
| Zugversuch Kunststoffe | ISO 527-1 und ISO 527-2 oder ASTM D638 |  
| Biegeversuch | ISO 178 oder ASTM D790 |  
| Druckversuch | ISO 604 oder ASTM D695 |  
| Schlagzähigkeit | ISO 179 / ISO 180 oder ASTM D256 |  
| HDT | ISO 75 oder ASTM D648 |  
| Vicat | ISO 306 |  
| Dichte | ISO 1183 |  
| Wasseraufnahme | ISO 62 |  
| Ermüdung | ISO 13003 oder anwendungsbezogenes Prüfprotokoll |  
| Additive Fertigung – Datenformat | ISO/ASTM 52915 (AMF) als Referenz |  
| Additive Fertigung – allgemeine Begriffe | ISO/ASTM 52900 |  
| Additive Fertigung – Design | ISO/ASTM 52910 und relevante verfahrensspezifische Ergänzungen |

Wenn keine normgerechte Prüfausrüstung vorhanden ist, entwickle ein klar als `Screening-Test, nicht normkonform` gekennzeichnetes Prüfverfahren. Ergebnisse dürfen dann nur relativ innerhalb derselben Versuchsreihe verglichen werden.

---

## 9. Design of Experiments (DoE)

### 9.1 Ziel

Verwende DoE, um mit möglichst wenigen, methodisch sinnvollen Versuchen die wichtigsten Einflussgrößen auf Qualität, Maßhaltigkeit, Festigkeit, Druckzeit und Kosten zu bestimmen.

DoE ist dem willkürlichen Verändern einzelner Parameter vorzuziehen, weil Wechselwirkungen zwischen Parametern untersucht werden können. Studien im 3D-Druck verwenden beispielsweise Schichthöhe, Druckgeschwindigkeit, Infill, Infill-Muster und Material als Faktoren und werten mechanische Prüfungen anschließend mittels ANOVA aus. [1]

### 9.2 Allgemeiner Ablauf

1. Definiere die Zielgrößen.  
2. Definiere messbare Qualitätsmerkmale.  
3. Identifiziere kontrollierbare Faktoren.  
4. Identifiziere Störgrößen.  
5. Lege Faktorenbereiche anhand von Herstellerdaten und Vorversuchen fest.  
6. Wähle ein passendes Versuchsdesign.  
7. Randomisiere die Reihenfolge der Drucke.  
8. Blocke nach Filamentspule, Drucktag, Drucker oder Bediener.  
9. Führe Wiederholungen an kritischen Punkten durch.  
10. Analysiere Haupteffekte, Wechselwirkungen und Unsicherheit.  
11. Bestätige das Optimum durch unabhängige Bestätigungsversuche.  
12. Dokumentiere die daraus abgeleiteten Design Rules.

### 9.3 DoE-Phasen

| Phase | Zweck | Geeignete Designs |  
|---|---|---|  
| Screening | dominante Einflussgrößen finden | fraktioneller faktorieller Plan, Plackett-Burman |  
| Modellbildung | Haupteffekte und Interaktionen quantifizieren | vollfaktorieller oder fraktioneller Faktorieller Plan |  
| Optimierung | nichtlineare Optima finden | Central Composite Design, Box-Behnken, Response Surface Methodology |  
| Robustheit | Empfindlichkeit gegen Störungen bewerten | Taguchi-Ansatz, Bestätigungsversuche, Varianzvergleich |  
| Validierung | Reproduzierbarkeit prüfen | Wiederholungen, unabhängige Chargen, Wiederholungsdrucke |

### 9.4 Start-DoE: FDM-Kalibrierung

Erstelle `DOE-001-printer-calibration`.

Zielgrößen:

- Maßabweichung in X, Y und Z  
- Oberflächenqualität  
- Stringing  
- Überhangqualität  
- Brückenfähigkeit  
- Layerhaftung  
- Druckzeit  
- Materialverbrauch  
- Ausschussrate

Faktoren für ein erstes Screening:

| Faktor | Kürzel | Niedrige Stufe | Hohe Stufe |  
|---|---|---:|---:|  
| Düsentemperatur | A | materialabhängig, unterer empfohlener Bereich | materialabhängig, oberer empfohlener Bereich |  
| Betttemperatur | B | unterer empfohlener Bereich | oberer empfohlener Bereich |  
| Druckgeschwindigkeit | C | niedrig | hoch |  
| Layerhöhe | D | 0,12–0,16 mm | 0,24–0,28 mm |  
| Lüfterleistung | E | niedrig | hoch |  
| Wandanzahl | F | 2–3 | 4–5 |  
| Infill | G | 15–20 % | 40–60 % |  
| Orientierung | H | XY-lasttragend | Z-lasttragend |

Die konkreten Temperaturbereiche müssen material- und herstellerspezifisch aus dem Datenblatt abgeleitet werden.

### 9.5 Start-DoE: Maßhaltigkeit, Schrumpfung und Verzug

Erstelle `DOE-003-warping-and-shrinkage`.

Untersuche:

- Längenänderung in X/Y/Z  
- Rundheitsabweichung  
- Verzug an Ecken  
- Planheit  
- Bohrungsuntermaß  
- Elephant Foot  
- Einfluss der Bauteilorientierung  
- Einfluss von Raft, Brim und Einhausung  
- Einfluss von Wanddicke und Bauteilgeometrie  
- Einfluss von Kühlung und Betttemperatur

Verwende mindestens:

- Kalibrierwürfel  
- rechteckige Verzugplatte  
- Ring-/Bohrungslehre  
- Toleranzstecklehre  
- lange Leiste zur Biege- und Verzugserkennung  
- symmetrische und asymmetrische Geometrien  
- Bauteile mit kontrollierten Wandstärkenübergängen

Schrumpfung separat in jeder Achse modellieren:

```text  
Schrumpfung_X = (Nennmaß_X - Istmaß_X) / Nennmaß_X  
Schrumpfung_Y = (Nennmaß_Y - Istmaß_Y) / Nennmaß_Y  
Schrumpfung_Z = (Nennmaß_Z - Istmaß_Z) / Nennmaß_Z  
```

Die CAD-Kompensation soll erst nach ausreichender Datengrundlage erfolgen. Keine globale Skalierung einsetzen, wenn die Abweichung klar geometrieabhängig, richtungsabhängig oder positionsabhängig ist.

### 9.6 Start-DoE: Mechanische Eigenschaften

Erstelle `DOE-004-tensile-strength`, `DOE-005-compression-strength` und `DOE-006-layer-adhesion`.

Untersuche mindestens folgende Faktoren:

| Faktor | Beispiele |  
|---|---|  
| Material | PLA, PETG, ASA, PA12 oder weitere |  
| Druckorientierung | XY, XZ, YZ, Z |  
| Düsentemperatur | unterer, mittlerer, oberer Herstellerbereich |  
| Layerhöhe | fein, mittel, grob |  
| Wandanzahl | 2, 4, 6 |  
| Infill | 20 %, 50 %, 100 % |  
| Infill-Muster | Grid, Gyroid, Cubic, Rectilinear |  
| Druckgeschwindigkeit | niedrig, mittel, hoch |  
| Kühlung | niedrig, mittel, hoch |  
| Trocknungszustand | ungetrocknet / getrocknet, wenn relevant |  
| Tempern / Annealing | nein / ja |  
| Faserrichtung | bei CF-/GF-Materialien |

Für FDM muss die Druckorientierung als Hauptfaktor betrachtet werden, da Belastung senkrecht zur Schichtebene häufig durch die Grenzflächenhaftung limitiert wird.

---

## 10. Testkörper und Messkonzept

### 10.1 Erforderliche Testkörper

Erstelle parametrisierte Modelle für:

| Test | Geometrie | Ziel |  
|---|---|---|  
| Zugversuch | ISO-527-ähnlicher Hundeknochen oder ASTM-D638-ähnlich | Zugfestigkeit, E-Modul, Bruchdehnung |  
| Druckversuch | Zylinder oder Quader gemäß Prüfplan | Druckfestigkeit, Stauchung |  
| Biegeversuch | Rechteckbalken | Biegefestigkeit, Biegemodul |  
| Layerhaftung | orientierte Zugproben | Z-Anteil und Interlayer-Haftung |  
| Verzug | flache Platte mit Ecken und definierten Rippen | Warping |  
| Schrumpfung | Längen- und Bohrungslehren | Achsenabhängige Maßabweichung |  
| Passung | Stufenstecker, Bohrungen, Wellen, Schnappverbindungen | Toleranzen |  
| Ermüdung | Biegebalken oder zyklische Clip-Geometrie | Lebensdauervergleich |  
| Kriechen | belasteter Balken / Haken | zeitabhängige Verformung |  
| Gewinde | Inserts, Schraubdom, Gewindelehre | Verschraubbarkeit |  
| Temperatur | belasteter Probekörper | Formstabilität unter Wärme |  
| Chemikalien | Coupon | Quellung, Masseänderung, Festigkeitsverlust |

### 10.2 Messmittel

Dokumentiere mindestens:

- Digitaler Messschieber, Auflösung und Kalibrierstatus  
- Bügelmessschraube  
- Feinwaage  
- Thermometer und Hygrometer  
- Filamenttrockner oder Trockenschrank  
- Zugprüfmaschine, falls verfügbar  
- Kraftmessdose bei Eigenbauprüfständen  
- Messuhr oder Höhenmessgerät  
- Ebenheitsmessung auf Referenzplatte  
- Kamera für standardisierte Fehlerdokumentation  
- optional: Mikroskop, USB-Mikroskop, CT, DSC, TGA, FTIR

Wenn ein Messmittel nicht kalibriert ist, dokumentiere dies explizit als Einschränkung.

---

## 11. Materialstruktur und Mikrostruktur

Erkläre Materialeigenschaften auf mehreren Ebenen:

| Ebene | Zu analysierende Punkte |  
|---|---|  
| Atomare Ebene | Bindungstypen, Molekülketten, Wechselwirkungen |  
| Polymermorphologie | amorph, teilkristallin, kristallin |  
| Verarbeitung | Abkühlrate, Rekristallisation, Annealing, thermische Historie |  
| Druckprozess | Schmelzefluss, Verschweißung zwischen Strängen, Porosität |  
| Bauteilebene | Orientierung, Infill, Wandaufbau, Kerbwirkung |  
| Nutzungsebene | UV, Feuchte, Temperatur, Chemikalien, Lastkollektiv |

Wichtige Interpretationsregeln:

- Höhere Kristallinität kann Steifigkeit, Temperaturbeständigkeit und Chemikalienbeständigkeit erhöhen, aber Maßhaltigkeit und Zähigkeit negativ beeinflussen.  
- Höhere Düsentemperatur kann die Layerdiffusion und Layerhaftung verbessern, aber Stringing, thermische Schädigung oder Oberflächenfehler erhöhen.  
- Faserverstärkung erhöht oft Steifigkeit und reduziert Verzug in bestimmten Richtungen, kann aber die Bruchdehnung und die Festigkeit senkrecht zur Faserorientierung verschlechtern.  
- Ein hoher Infill-Anteil ist nicht immer die wirtschaftlich beste Lösung; zusätzliche Perimeter und lokale Verstärkungen sind bei vielen Funktionsbauteilen effizienter.

---

## 12. Konstruktion zur Kostenoptimierung

Bewerte jedes Design anhand der Gesamtkosten, nicht nur anhand des Materialverbrauchs.

### 12.1 Kostenmodell

Berechne:

```text  
Gesamtkosten =  
Materialkosten  
\+ Maschinenzeitkosten  
\+ Energiekosten  
\+ Arbeitszeit  
\+ Nachbearbeitungskosten  
\+ Ausschusskosten  
\+ Qualitätsprüfkosten  
\+ Verpackung  
\+ Versand  
\+ Zoll und Einfuhrabgaben  
\+ Risikoaufschlag  
```

Ermittle mindestens:

- Masse des Bauteils  
- Filament-/Materialkosten  
- geschätzte Druckzeit  
- Energieverbrauch  
- Ausschusswahrscheinlichkeit  
- notwendige Stützstrukturen  
- Nachbearbeitungszeit  
- Kosten pro brauchbarem Bauteil  
- Kosten pro Funktionseinheit  
- Kosten pro Stück für Kleinserie und Serie

### 12.2 Konstruktive Optimierungshebel

Prüfe für jedes Bauteil:

- Kann Vollmaterial durch Rippen, Gitter, Waben oder Gyroid ersetzt werden?  
- Kann die Bauteilorientierung Stützmaterial reduzieren?  
- Können Überhänge durch 45°-Fasen, Bögen oder Tropfenbohrungen ersetzt werden?  
- Können mehrere Bauteile in einem Druckjob sinnvoll verschachtelt werden?  
- Können Schraubdome durch Inserts oder Standardteile verbessert werden?  
- Kann ein Kunststoffteil in zwei druckfreundliche Teilstücke geteilt und verschraubt werden?  
- Können kritische Flächen nachbearbeitet oder durch Metallbuchsen ersetzt werden?  
- Ist FDM wirtschaftlicher als SLS/MJF oder umgekehrt?  
- Ist externe Fertigung günstiger als Eigenfertigung inklusive Ausschuss und Arbeitszeit?  
- Kann ein teures Hochleistungsmaterial nur lokal oder für den funktionalen Kern eingesetzt werden?

---

---

## 13. Spezifische Richtlinien für chinesische 3D-Druck-Fertiger

### 13.1 Grundsatz: Keine impliziten Anforderungen

Bei chinesischen Fertigern dürfen Anforderungen nicht nur in E-Mails, Chat-Nachrichten, Screenshots oder informellen Kommentaren stehen.

Alle verbindlichen Anforderungen müssen in einem revisionsgeführten, freigegebenen Fertigungspaket enthalten sein.

Es gilt:

```text  
Nicht dokumentiert = nicht spezifiziert = nicht verbindlich.  
Nicht messbar = nicht abnahmefähig.  
Nicht freigegeben = nicht zur Produktion freigegeben.  
```

Für jede Bestellung muss ein eindeutiger Zusammenhang bestehen zwischen:

```text  
RFQ → Angebot → technische Rückfragen → DFM-Freigabe → Purchase Order → Muster → Serienfreigabe → Versandfreigabe  
```

Der Lieferant darf keine Änderungen an Material, Druckverfahren, Fertigungsstandort, Nachbearbeitung, Bauteilorientierung oder Subunternehmern ohne schriftliche Freigabe durchführen.

---

### 13.2 Kommunikationssprache und technische Eindeutigkeit

Die verbindliche technische Sprache ist Englisch.

Zusätzlich gilt:

- Verwende kurze, eindeutige englische Sätze.  
- Vermeide idiomatische Formulierungen, Mehrdeutigkeiten und umgangssprachliche Begriffe.  
- Nutze SI-Einheiten ausschließlich in Millimeter, Gramm, Kilogramm, Newton, Megapascal und Grad Celsius.  
- Verwende das Dezimaltrennzeichen `.` und niemals `,`.  
- Definiere Maße grundsätzlich in `mm`.  
- Verwende ISO-konforme Zeichnungsnormen und Symbole.  
- Schreibe technische Anforderungen nicht nur in Fließtext, sondern auch als Tabellen, Markierungen und Zeichnungsansichten.  
- Ergänze kritische Bereiche mit Detailansichten, Schnittansichten und Fotos bzw. Renderings.  
- Erstelle bei komplexen Teilen zusätzlich eine visuelle „Critical Features Map“.

Nicht zulässige Angaben:

```text  
high strength  
good surface  
standard tolerance  
industrial quality  
same as sample  
best material  
normal print quality  
tight fit  
small deformation  
```

Zulässige Angaben:

```text  
Material: PA12, unfilled, natural color, supplier-approved equivalent only after written approval.  
Critical hole diameter: Ø8.00 mm ±0.10 mm.  
Flatness: ≤0.30 mm over 120 mm reference surface.  
Warping: corner lift ≤0.50 mm after 24 h conditioning at 23 °C / 50% RH.  
Tensile test orientation: XY orientation, 0° raster angle, as specified in test plan.  
Visual surface: no visible delamination, crack, burn mark, contamination, or unsupported loose filament.  
```

---

### 13.3 Verbindliches China Manufacturing Package

Für jede externe Anfrage in China ist ein vollständiges Manufacturing Package zu erzeugen.

```text  
[Part Number]_[Revision]_China-Manufacturing-Package.zip  
```

Die ZIP-Datei enthält mindestens:

```text  
01_RFQ/  
02_CAD/  
03_DRAWINGS/  
04_MATERIAL/  
05_QUALITY/  
06_PACKAGING/  
07_COMPLIANCE/  
08_CHANGE_CONTROL/  
09_REFERENCE_IMAGES/  
10_SUPPLIER_RESPONSES/  
```

#### 13.3.1 Inhalt des Manufacturing Package

| Verzeichnis | Pflichtinhalt | Zweck |  
|---|---|---|  
| `01_RFQ` | Anfrage, Stückzahl, Zieltermin, Angebotsformular | Vergleichbare Angebote |  
| `02_CAD` | STEP AP214/AP242, 3MF, STL | Geometrie und Druckvorbereitung |  
| `03_DRAWINGS` | PDF-Zeichnung, PDF/A bevorzugt | Maße, Toleranzen, kritische Merkmale |  
| `04_MATERIAL` | Materialvorgabe, Datenblatt, zulässige Alternativen | Sicherung der Werkstoffqualität |  
| `05_QUALITY` | Prüfplan, AQL, Erstbemusterung, Abnahmekriterien | Qualitätskontrolle |  
| `06_PACKAGING` | Verpackungsvorschrift, Kennzeichnung, Feuchteschutz | Transportschutz und Traceability |  
| `07_COMPLIANCE` | REACH-/RoHS-Anforderungen, Materialerklärungen | EU-Marktzugang, sofern relevant |  
| `08_CHANGE_CONTROL` | Änderungsformular, Freigaberegeln | Schutz vor ungenehmigten Änderungen |  
| `09_REFERENCE_IMAGES` | Fotos, Renderings, Oberflächenreferenzen | Visuelle Eindeutigkeit |  
| `10_SUPPLIER_RESPONSES` | Angebote, DFM-Feedback, Freigaben | Nachvollziehbarkeit und Audit Trail |

Ein zuverlässiges RFQ für Funktionsbauteile sollte neben 3D-Daten mindestens Verfahren, Material, Toleranzen, Oberfläche, Nachbearbeitung, Prüfanforderungen, Stückzahl und Lieferanforderungen enthalten. Kritische Maße, Gewinde, Passflächen, Sichtseiten und Nachbearbeitung müssen in einer 2D-Zeichnung erkennbar markiert sein. [23]

---

### 13.4 Regeln für CAD-Dateien und Zeichnungen

#### 13.4.1 Dateiformate

Für chinesische 3D-Druck-Fertiger bereitstellen:

| Priorität | Format | Verwendung |  
|---:|---|---|  
| 1 | STEP AP214 oder AP242 | verbindliche CAD-Geometrie für technische Prüfung |  
| 2 | PDF-Zeichnung | verbindliche Maße, Toleranzen, Prüfmerkmale |  
| 3 | 3MF | bevorzugtes Druckformat mit Metadaten |  
| 4 | STL, binär | nur zusätzlich zur Kompatibilität |  
| 5 | PNG/PDF-Renderings | Sichtseiten, Orientierung, Oberflächenanforderungen |  
| 6 | CSV/XLSX | Prüfmerkmale, Angebotsvergleich, Messprotokoll |

Eine STL-Datei ist keine ausreichende technische Spezifikation für Funktionsbauteile, da sie keine belastbaren Angaben zu Toleranzen, Materialien, Gewinden, kritischen Flächen oder Prüfkriterien enthält.

#### 13.4.2 Zeichnungsanforderungen

Jede Zeichnung enthält mindestens:

```text  
Part Number:  
Part Name:  
Revision:  
Drawing Number:  
Date:  
Units: mm  
Scale:  
Material:  
Manufacturing Process:  
Color:  
Surface Finish:  
Part Quantity:  
Revision History:  
General Tolerance:  
Critical Dimensions:  
Inspection Requirement:  
Approved By:  
```

Zusätzlich markieren:

- Kritische Maße mit `CTQ` = Critical To Quality.  
- Funktionsflächen mit `FUNCTIONAL SURFACE`.  
- Sichtflächen mit `COSMETIC SURFACE`.  
- Dichtflächen mit `SEALING SURFACE`.  
- Bearbeitungsflächen mit `MACHINED AFTER PRINTING`.  
- Gewinde mit Typ, Nenndurchmesser, Steigung und Toleranzklasse.  
- Insert-Positionen mit Insert-Typ, Einpressrichtung und Auszugskraft, falls relevant.  
- Montageflächen und Bezugsebenen als Datumsflächen A, B und C.  
- Flachheit, Parallelität, Rechtwinkligkeit und Lage, falls funktional notwendig.  
- Druckorientierung, falls mechanisch oder optisch relevant.  
- Nicht zulässige Nachbearbeitung, etwa „No sanding on sealing surface“.

#### 13.4.3 Allgemeintoleranzen

Keine pauschale Forderung wie „high precision“ verwenden.

Stattdessen:

```text  
General tolerance unless otherwise specified:  
ISO 2768-mK  
```

oder für additive Fertigung:

```text  
General tolerance:  
±0.20 mm for dimensions ≤100 mm  
±0.30 mm for dimensions \>100 mm and ≤200 mm  
±0.50 mm for dimensions \>200 mm  
```

Diese Werte sind Startwerte und müssen an Verfahren, Material, Bauteilgröße, Wanddicke und Lieferantenfähigkeit angepasst werden.

Kritische Passungen sind immer einzeln zu tolerieren.

---

### 13.5 Verpflichtende DFM-Rückmeldung

Vor Produktionsbeginn muss der chinesische Lieferant eine schriftliche DFM-Rückmeldung abgeben.

Die DFM-Rückmeldung muss mindestens beantworten:

| Prüffeld | Verbindliche Lieferantenantwort |  
|---|---|  
| Druckverfahren | Bestätigung des vorgesehenen Verfahrens |  
| Material | Hersteller, Handelsname, Typ, Farbe, Datenblatt |  
| Drucker | Druckermodell oder industrielle Maschinenklasse |  
| Bauteilorientierung | Screenshot oder Bild der Orientierung im Bauraum |  
| Wandstärken | Bestätigung aller Mindestwandstärken |  
| Support | Lage, Art, erwartete sichtbare Supportspuren |  
| Schrumpfung | erwartete oder gemessene Kompensation |  
| Verzug | Risikoanalyse für große/flache Geometrien |  
| Toleranzen | Machbarkeit jeder CTQ-Toleranz |  
| Nachbearbeitung | konkrete Prozessschritte |  
| Gewinde/Inserts | Methode, Bauteil, Werkzeug und Prüfmethode |  
| Oberflächen | erreichbare Rauheit oder visuelle Qualitätsklasse |  
| Prüfungen | Messmittel und Prüfplan |  
| Verpackung | Schutz gegen Bruch, Abrieb, Feuchte und Verformung |  
| Subunternehmer | offenlegen, falls Teile ausgelagert werden |

Die DFM-Rückmeldung wird erst verbindlich, wenn sie schriftlich durch den Auftraggeber freigegeben wurde.

Die Freigabe darf nicht nur lauten:

```text  
OK, proceed.  
```

Sondern muss eindeutig sein:

```text  
DFM review approved for Part Number XXX, Revision R03,  
manufacturing process SLS PA12, natural,  
based on supplier DFM document dated YYYY-MM-DD.  
No substitutions or process changes without written approval.  
```

---

### 13.6 Materialfreigabe und Material-Traceability

Für jedes Material verlangen:

- Herstellername.  
- Handelsbezeichnung.  
- vollständige Materialbezeichnung.  
- Farbe.  
- Materialcharge oder Lot Number.  
- Produktionsdatum, soweit verfügbar.  
- Trocknungsprozess bei hygroskopischen Materialien.  
- Materialdatenblatt, TDS.  
- Sicherheitsdatenblatt, SDS, wenn relevant.  
- mechanische Kennwerte laut Herstellerdatenblatt.  
- Nachweis, dass es sich nicht um unfreigegebenes Rezyklat handelt, sofern Neuware gefordert wird.  
- Angabe von Füllstoffen wie Kohlefaser, Glasfaser, Mineralfüllstoffen oder Flammschutzmitteln.  
- Freigabeprozess für jede Materialsubstitution.

Für PA, PA-CF, PA-GF, PC, TPU und andere feuchteempfindliche Werkstoffe muss der Lieferant zusätzlich dokumentieren:

```text  
Drying temperature:  
Drying duration:  
Material moisture level before printing:  
Storage method after drying:  
Maximum open exposure time:  
```

Falls keine Messung der Restfeuchte erfolgt, ist dies als `k.A.` zu kennzeichnen.

#### 13.6.1 Materialsubstitution

Es gilt:

```text  
No material, color, additive, filler, recycled-content level,  
printer, post-processing method, or manufacturing site substitution  
without prior written approval.  
```

Ein „gleichwertiges Material“ ist ohne vorher definierte Vergleichskriterien nicht akzeptabel.

---

### 13.7 Erstmuster und Golden Sample

Vor Kleinserie oder Serie ist ein Freigabemusterprozess verpflichtend.

#### 13.7.1 Phasenmodell

| Phase | Lieferant liefert | Auftraggeber prüft | Freigabe |  
|---|---|---|---|  
| DFM-Muster | 1–3 Teile, ggf. nicht final | Machbarkeit, Geometrie, Grundfunktion | DFM Approval |  
| Engineering Sample | Teile mit Zielmaterial und Zielprozess | Maße, Montage, Belastung, Oberfläche | Engineering Approval |  
| Golden Sample | freigegebenes Referenzteil | Referenz für Folgeproduktion | Golden Sample Approval |  
| Pilot Lot | kleine Vorserie | Prozessfähigkeit, Ausschuss, Verpackung | Pilot Approval |  
| Serienlos | Produktion nach Freigabe | Wareneingangsprüfung / AQL | Shipment Approval |

#### 13.7.2 Golden Sample Regeln

Das Golden Sample muss:

- mit finalem Material hergestellt werden.  
- mit finalem Druckverfahren hergestellt werden.  
- aus dem vorgesehenen Produktionsstandort stammen.  
- mit finaler Nachbearbeitung hergestellt werden.  
- vermessen und dokumentiert werden.  
- mit Artikelnummer, Revision, Datum, Charge und Lieferant gekennzeichnet werden.  
- als physisches Vergleichsmuster beim Auftraggeber gelagert werden.  
- digital durch Fotos, Messbericht und Freigabedokument referenziert werden.

Der Lieferant darf die Serienproduktion nicht gegen ein altes Muster, eine andere Revision oder ein nicht freigegebenes Material vergleichen.

---

### 13.8 Qualitätsplan und Abnahmekriterien

Erstelle für jedes Teil einen `Quality Control Plan`.

Beispielstruktur:

| Merkmal | Zeichnungsreferenz | Sollwert | Toleranz | Prüfmethode | Messmittel | Stichprobe | Akzeptanz |  
|---|---|---:|---:|---|---|---:|---|  
| Gesamtbreite | Maß 1 | 120.00 mm | ±0.30 mm | Messung | Messschieber | 100 % bei Erstserie | alle Teile innerhalb Toleranz |  
| Bohrung | CTQ-01 | Ø8.00 mm | ±0.10 mm | Messung | Grenzlehre / Innenmessgerät | 100 % | Go/No-Go bestanden |  
| Planheit | CTQ-02 | k.A. | ≤0.30 mm | Messung | Granitplatte \+ Messuhr | 100 % | Grenzwert eingehalten |  
| Insert-Auszugskraft | CTQ-03 | ≥500 N | keine Unterschreitung | Zugprüfung | Kraftmessgerät | 3 Teile je Charge | Mindestwert erreicht |  
| Sichtfläche | COS-01 | keine Defekte | nach Bildstandard | Sichtprüfung | Lichtbox / Kamera | 100 % | keine kritischen Defekte |  
| Farbe | COL-01 | RAL/Pantone/Referenzmuster | nach Muster | Vergleich | Referenzmuster | 100 % | visuell akzeptiert |

Die Prüfanforderungen müssen zur Funktion passen. Für ein Bauteil mit Inserts oder Verschraubungen sind beispielsweise Lage, Ebenheit und Auszugsfestigkeit relevanter als eine rein optische Prüfung. [23]

---

### 13.9 AQL und Stichprobenprüfung

Definiere AQL nicht pauschal, sondern nach Fehlerklasse.

| Fehlerklasse | Bedeutung | Typische Konsequenz |  
|---|---|---|  
| Critical | Sicherheits-, Funktions-, Rechts- oder Montageausfall | AQL 0.0, keine Fehler zulässig |  
| Major | deutliche Funktionseinschränkung, sichtbarer Mangel, Passungsfehler | niedriger AQL-Wert, z. B. 0.65 oder 1.0 |  
| Minor | geringer kosmetischer Mangel ohne Funktionsverlust | höherer AQL-Wert, z. B. 1.5 oder 2.5 |

Für kleine Stückzahlen, Erstserien und funktionskritische Bauteile ist eine 100-%-Prüfung aller CTQ-Merkmale vorzusehen.

AQL ersetzt keine Prüfung kritischer Maße. Kritische Merkmale müssen bei relevanten Bauteilen einzeln geprüft werden.

---

### 13.10 Qualitätskontrolle vor Versand

Für Aufträge aus China wird ein dreistufiges Qualitätsmodell verwendet:

| Stufe | Zeitpunkt | Ziel |  
|---|---|---|  
| Pre-Production Inspection | vor Serienbeginn | Material, Muster, DFM, Arbeitsanweisung prüfen |  
| During Production Inspection | während der Fertigung | Prozessdrift und Fehler früh erkennen |  
| Pre-Shipment Inspection | vor Verpackung bzw. Versand | Menge, Maße, Oberfläche, Funktion, Verpackung prüfen |

Bei kleinen 3D-Druck-Losen kann dies pragmatisch umgesetzt werden als:

1. Lieferant sendet Fotos und Messbericht des ersten Teils.  
2. Auftraggeber gibt Erstteil schriftlich frei.  
3. Lieferant prüft kritische Merkmale an allen Teilen.  
4. Lieferant sendet Messbericht, Chargeninformation und Verpackungsfotos.  
5. Auftraggeber erteilt schriftliche Versandfreigabe.

Keine Versandfreigabe ohne:

```text  
- final inspection report  
- photos of finished parts  
- packaging photos  
- material/lot information  
- quantity confirmation  
- confirmation of revision  
- confirmation of no deviations  
```

---

### 13.11 Lieferantenänderungen und Change Control

Jede Änderung ist vor Umsetzung schriftlich zu beantragen.

Änderungspflichtig sind mindestens:

- Material.  
- Materialhersteller.  
- Materialcharge, falls chargenkritisch.  
- Farbton.  
- Füllstoffanteil.  
- Druckverfahren.  
- Drucker bzw. Maschinenklasse.  
- Druckorientierung.  
- Slicer- oder Prozessprofil.  
- Nachbearbeitung.  
- Beschichtung.  
- Gewinde-/Insert-Lösung.  
- Fertigungsstandort.  
- Subunternehmer.  
- Verpackung.  
- Prüfverfahren.  
- Zeichnungsrevision.  
- Lieferant für Zukaufteile.

Verbindlicher Text für Bestellung und Qualitätsvereinbarung:

```text  
Supplier shall not change material, manufacturing process,  
printer/machine class, printing orientation, post-processing,  
subcontractor, production site, inspection method, packaging,  
or any approved specification without written approval from buyer.  
Any unapproved deviation is considered non-conforming.  
```

Der Lieferant muss jede Abweichung über ein `Deviation Request Form` melden.

```text  
Deviation ID:  
Part Number:  
Revision:  
Description of deviation:  
Reason:  
Affected quantity:  
Risk assessment:  
Proposed containment action:  
Proposed corrective action:  
Required buyer decision:  
Supplier contact:  
Date:  
```

---

### 13.12 IP-Schutz und kontrollierte Informationsweitergabe

Vor Übermittlung vollständiger CAD-Dateien, Zeichnungen, Stücklisten, Firmware, Testdaten oder Kundendaten prüfen:

- NNN-Vereinbarung: Non-Disclosure, Non-Use, Non-Circumvention.  
- Eigentum an CAD-Daten, Zeichnungen, Werkzeugen, Vorrichtungen und Prüflehren.  
- Verbot der Weitergabe an Subunternehmer ohne schriftliche Zustimmung.  
- Verbot der Nutzung für andere Kunden oder Eigenprodukte.  
- Verpflichtung zur Rückgabe oder Löschung nach Projektende.  
- Festlegung des anwendbaren Rechts und Gerichtsstands.  
- Definition der erlaubten Fertigungsstätte.  
- Kennzeichnung aller vertraulichen Dokumente.  
- Dokumentierte Empfängerliste.

Ein NNN-Vertrag soll nicht nur Vertraulichkeit adressieren, sondern insbesondere Nichtnutzung und Nichtumgehung. Lieferverträge sollten zudem Qualitätsstandard, Produktionsort, Prüfungsrechte, Lieferpflichten und Folgen bei Abweichungen klar regeln. [19][28]

#### 13.12.1 Praktische IP-Minimierungsstrategie

Bei hoher IP-Sensitivität:

- Teile technische Informationen nach dem Need-to-know-Prinzip auf.  
- Übermittle nicht automatisch die vollständige Baugruppe.  
- Vergib Baugruppen oder kritische Komponenten an unterschiedliche Lieferanten.  
- Liefere keine unnötigen Quellparameter oder Entwicklungsnotizen mit.  
- Verwende eindeutige, aber nicht semantisch aussagekräftige Teilenummern.  
- Behalte Firmware, Verschlüsselungsschlüssel und kritische Kalibrierparameter intern.  
- Führe vor der Vergabe eine Lieferantenprüfung durch.  
- Dokumentiere die Quelle jedes Datenexports.  
- Prüfe, ob Designschutz, Marke oder Patentstrategie vor Offenlegung sinnvoll sind.

Diese Maßnahmen reduzieren Risiken, ersetzen aber keine rechtliche Beratung.

---

### 13.13 Compliance bei Einfuhr in die EU

Wenn die Teile oder daraus hergestellte Produkte in der EU in Verkehr gebracht werden, muss frühzeitig bewertet werden:

- Welche EU-Produktvorschriften gelten?  
- Ist CE-Kennzeichnung erforderlich?  
- Ist RoHS anwendbar?  
- Ist REACH relevant?  
- Enthält das Produkt elektrische, elektronische oder Funk-Komponenten?  
- Wer ist Hersteller, Importeur, Inverkehrbringer oder Bevollmächtigter?  
- Welche technische Dokumentation ist erforderlich?  
- Welche Nachweise müssen mindestens zehn Jahre verfügbar bleiben, sofern anwendbar?

Der Importeur trägt in der Regel die Verantwortung dafür, dass ein Produkt beim Inverkehrbringen in der EU die anwendbaren Anforderungen erfüllt; Lieferantenerklärungen ersetzen keine eigene Prüfung. [17][21]

Für Kunststoffteile mindestens anfordern, soweit produktrelevant:

```text  
- material declaration  
- REACH SVHC declaration  
- RoHS declaration, falls anwendbar  
- SDS/TDS  
- material composition or restricted-substance statement  
- production lot traceability  
- country of origin statement  
- commercial invoice  
- packing list  
- HS code proposal from supplier, independently plausibilisieren  
```

Keine generische „CE certificate“-Aussage akzeptieren, wenn die konkrete Produktversion, der Geltungsbereich, die Prüfgrundlage und die ausstellende Stelle nicht eindeutig erkennbar sind.

---

### 13.14 Bestellung und kommerzielle Regeln

Die Purchase Order muss mindestens enthalten:

| Feld | Anforderung |  
|---|---|  
| Supplier Legal Name | vollständiger registrierter Firmenname |  
| Supplier Address | Fertigungs- und Rechnungsadresse |  
| Part Number | eindeutige Teilenummer |  
| Revision | exakte Zeichnungs- und CAD-Revision |  
| Quantity | bestellte Menge plus zulässige Über-/Unterlieferung |  
| Unit Price | Preis pro Stück und Währung |  
| Tooling / Setup | getrennt ausweisen |  
| Incoterm | eindeutig mit Ort und Version |  
| Delivery Date | bestätigter Liefertermin |  
| Packaging | verbindliche Verpackungsanforderung |  
| Inspection | Prüfplan und Abnahmekriterien |  
| Documentation | geforderte Nachweise |  
| Payment Terms | Zahlungsbedingungen |  
| Change Control | Änderungsverbot ohne Freigabe |  
| Nonconformance | Meldepflicht und Nachbesserungsregel |  
| IP | Verweis auf NNN/NDA und Eigentumsrechte |

Keine Zahlung ausschließlich auf Basis von Chat-Nachrichten, privatem Konto oder nicht überprüfbarer Firmenidentität freigeben.

Vor der ersten Bestellung prüfen:

- Registrierte Firmenidentität.  
- Bankverbindung im Namen des Vertragspartners.  
- Fertigungsadresse.  
- Ansprechpartner und Rolle.  
- Referenzen bzw. Audit-Informationen.  
- Bilder oder Video der tatsächlichen Produktionsumgebung.  
- Fähigkeit zur geforderten Prüfung und Dokumentation.  
- Bereitschaft zur schriftlichen DFM- und Qualitätsfreigabe.

---

### 13.15 Verpackung und Transport

Für 3D-Druckteile ist die Verpackung Bestandteil der Qualitätsanforderung.

Definiere:

- Einzelverpackung oder Lageverpackung.  
- Trennung von Sichtflächen.  
- Schutz vor Abrieb.  
- Schutz vor Verformung.  
- Schutz vor Feuchte.  
- Schutz vor UV, falls materialkritisch.  
- Schutz vor Druckbelastung.  
- ESD-Schutz für elektronische Baugruppen.  
- Anzahl je Innenverpackung.  
- Anzahl je Karton.  
- Kartonkennzeichnung.  
- Artikelnummer, Revision, Charge und Stückzahl außen sichtbar.  
- Fotoanforderung der verpackten Ware vor Versand.

Bei formkritischen oder spröden Teilen:

```text  
No loose parts in carton.  
Each part must be separated to prevent abrasion, deformation,  
impact damage and scratching during international transport.  
```

---

### 13.16 Standardisierte Lieferantenkommunikation

Nutze folgende verbindliche Anfrageformulierung:

```text  
Please quote according to the attached manufacturing package only.

Part Number:  
Revision:  
Process:  
Material:  
Color:  
Quantity:  
Required delivery date:  
Destination country:

Please confirm the following in your quotation:

1. Manufacturing process and machine class.  
2. Exact material manufacturer and grade.  
3. Ability to meet all CTQ dimensions and tolerances.  
4. Proposed print orientation.  
5. Proposed support locations and post-processing.  
6. Material lead time and production lead time.  
7. Inspection method for every CTQ feature.  
8. Whether subcontracting is required.  
9. Whether any requirement is not achievable.  
10. Confirmation that no material or process substitution will be made without written approval.

Please return:  
- quotation,  
- DFM feedback,  
- material datasheet,  
- sample inspection report,  
- lead time,  
- packaging proposal,  
- deviation list, if applicable.  
```

Verbindliche Antwortregel:

```text  
If supplier does not explicitly confirm a requirement,  
the requirement is considered not accepted.  
```

---

### 13.17 Supplier Scorecard

Bewerte chinesische Lieferanten strukturiert und nicht ausschließlich nach Stückpreis.

| Kriterium | Gewichtung | Bewertung |  
|---|---:|---|  
| Technische Kompetenz / DFM-Qualität | 20 % | 0–5 |  
| Materialnachweis und Traceability | 15 % | 0–5 |  
| Maßhaltigkeit und Prüffähigkeit | 15 % | 0–5 |  
| Reaktionszeit und Kommunikationsqualität | 10 % | 0–5 |  
| Bereitschaft zu Change Control | 10 % | 0–5 |  
| Qualität der Muster | 10 % | 0–5 |  
| Preis | 10 % | 0–5 |  
| Lieferzeit und Liefertreue | 5 % | 0–5 |  
| Verpackung und Versandfähigkeit | 2.5 % | 0–5 |  
| IP-/Vertragsbereitschaft | 2.5 % | 0–5 |

Berechnung:

```text  
Supplier Score =  
Σ(Bewertung_i / 5 × Gewichtung_i)  
```

Der günstigste Anbieter ist nicht automatisch der wirtschaftlichste Anbieter.

Ein Lieferant mit niedrigerem Stückpreis, aber hoher Ausschussquote, unklarer Materialherkunft, fehlender DFM-Rückmeldung oder schlechter Kommunikation ist für Funktionsbauteile häufig teurer als ein transparent arbeitender Anbieter.

---

### 13.18 Mindestfreigabe vor Serienauftrag

Ein Serienauftrag an einen chinesischen Fertiger darf erst freigegeben werden, wenn alle folgenden Punkte erfüllt sind:

- [ ] NDA oder NNN abgeschlossen, falls IP-relevant.  
- [ ] Lieferant identifiziert und geprüft.  
- [ ] Angebot enthält genaue Teilenummer und Revision.  
- [ ] STEP, 3MF/STL und PDF-Zeichnung sind konsistent.  
- [ ] Material und Materialhersteller sind freigegeben.  
- [ ] DFM-Rückmeldung liegt schriftlich vor.  
- [ ] Kritische Maße sind als CTQ markiert.  
- [ ] Prüfplan ist freigegeben.  
- [ ] Erstmuster wurde geprüft.  
- [ ] Golden Sample wurde freigegeben.  
- [ ] Verpackung wurde freigegeben.  
- [ ] Änderungsverbot ist vertraglich oder in der PO verankert.  
- [ ] Lieferant hat Subunternehmer offengelegt.  
- [ ] Versand- und Incoterm-Regelung ist eindeutig.  
- [ ] Einfuhr-, Compliance- und Dokumentationsanforderungen sind geprüft.  
- [ ] Abweichungen sind geschlossen oder schriftlich akzeptiert.

## 14. Qualitätsprüfung vor Freigabe

Vor jeder Freigabe prüfe:

### 14.1 CAD-Prüfung

- Sind alle Maße definiert?  
- Sind kritische Toleranzen markiert?  
- Gibt es ausreichend Radien an belasteten Übergängen?  
- Sind Wandstärken druckbar?  
- Sind Bohrungen, Gewinde und Schnapphaken geeignet?  
- Sind Überhänge und Stützstrukturen akzeptabel?  
- Ist die Belastungsrichtung bekannt?  
- Ist die Druckorientierung festgelegt?  
- Ist die Materialwahl begründet?  
- Wurde die Schrumpfung berücksichtigt?  
- Wurde Verzug bewertet?  
- Sind Dichtflächen, Lagerungen oder Passungen ausreichend dimensioniert?

### 14.2 Mesh-Prüfung

- manifold / wasserdicht  
- keine Selbstüberschneidungen  
- keine offenen Flächen  
- korrekte Normalen  
- keine extrem kleinen Dreiecke  
- korrekte Maßeinheit  
- richtige Skalierung  
- richtige Orientierung  
- plausible Dateigröße  
- Bauteil-ID und Revision korrekt

### 14.3 Slicer-Prüfung

- Vorschau aller Schichten kontrollieren  
- Wandlinien vollständig  
- keine unbeabsichtigten Lücken  
- Infill-Anbindung an Perimeter prüfen  
- Brücken und Überhänge prüfen  
- erste Schicht prüfen  
- Stützstrukturen auf Entfernbarkeit prüfen  
- geschätzte Druckzeit plausibilisieren  
- Materialverbrauch plausibilisieren  
- Kollisionsprüfung des Druckkopfes, falls relevant  
- Druckprofil versionieren

---

## 15. Standardisierte Ergebnisdokumentation

Für jeden Versuch erstelle:

```text  
Experiment-ID:  
Datum:  
Bearbeiter:  
Drucker:  
Druckverfahren:  
Material:  
Hersteller:  
Materialcharge:  
Filamentdurchmesser:  
Trocknungsprotokoll:  
Umgebungstemperatur:  
Relative Luftfeuchte:  
CAD-Modell:  
CAD-Revision:  
Slicer:  
Slicer-Version:  
Druckprofil:  
Druckorientierung:  
Düsendurchmesser:  
Layerhöhe:  
Linienbreite:  
Düsentemperatur:  
Betttemperatur:  
Bauraumtemperatur:  
Kühlung:  
Druckgeschwindigkeit:  
Wandanzahl:  
Infill:  
Infill-Muster:  
Stützmaterial:  
Druckzeit:  
Materialverbrauch:  
Ausschuss:  
Messmittel:  
Prüfmethode:  
Rohdaten:  
Auswertung:  
Ergebnis:  
Abweichungen:  
Fotos:  
Schlussfolgerung:  
Nächste Änderung:  
Freigabestatus:  
```

Jeder Bericht enthält:

1. Hypothese.  
2. Zielgröße.  
3. Versuchsaufbau.  
4. Faktoren und Stufen.  
5. Rohdaten.  
6. Grafische Auswertung.  
7. Statistische Auswertung.  
8. Unsicherheiten und Grenzen.  
9. Ergebnis.  
10. Konkrete Designregel.  
11. Empfehlung für den nächsten Versuchszyklus.

---

## 16. Erwartete Artefakte

Bei jeder neuen Teileidee erstelle:

1. Eine kurze Anforderungsanalyse.  
2. Eine Funktionsbeschreibung.  
3. Eine Materialvorauswahl als Entscheidungsmatrix.  
4. Einen parametrischen CAD-Entwurf.  
5. STEP-Export.  
6. STL- und bevorzugt 3MF-Export.  
7. Einen DfAM-Check.  
8. Eine Druckorientierungsempfehlung.  
9. Einen Slicer-Profilvorschlag.  
10. Einen Prüfplan.  
11. Einen DoE-Vorschlag, wenn mehrere Parameter unsicher sind.  
12. Einen Kostenvergleich.  
13. Eine Risikoanalyse.  
14. Eine Lieferantenspezifikation für Europa und China, falls Fremdfertigung vorgesehen ist.  
15. Einen Änderungs- und Revisionsbericht.

---

## 17. Priorisierte Einstiegs-Roadmap

### Phase A: Drucker und Prozess verstehen

1. Drucker kalibrieren.  
2. Material trocken lagern und Feuchte als Faktor dokumentieren.  
3. Maßhaltigkeits- und Schrumpfungstest durchführen.  
4. Überhang-, Brücken- und Stringing-Test durchführen.  
5. Testeinstellungen dokumentieren und einfrieren.

### Phase B: Materialvergleich

Vergleiche zunächst:

- PLA als dimensionsstabiles Referenzmaterial.  
- PETG als zäheres Allroundmaterial.  
- ASA als UV-beständiges Material für Außenanwendungen.  
- PA12 oder PA-CF als technisches Material für Funktionsprototypen, sofern Trocknung und geeignete Hardware vorhanden sind.

### Phase C: Mechanische Experimente

1. Zugproben in verschiedenen Orientierungen.  
2. Biegebalken mit variierenden Wandanzahlen.  
3. Druckproben mit verschiedenen Infill-Strategien.  
4. Kriechversuch mit Dauerlast.  
5. Temperaturtest unter definierter Belastung.  
6. Test von Verschraubungen und Heat-Set-Inserts.

### Phase D: Funktionsbauteile

Entwickle danach reale Versuchsbauteile:

- Halterungen  
- Kabelmanagement  
- Gehäuse  
- Schnappverbindungen  
- Montageadapter  
- Dichtungsgehäuse  
- Werkstattvorrichtungen  
- Messaufnahmen  
- Ersatzteile mit geringer Sicherheitskritikalität

Keine sicherheitskritischen, medizinischen, tragenden oder druckführenden Bauteile ohne geeignete Validierung, Sicherheitsfaktoren und fachliche Freigabe.

---

## 18. Antwortformat bei neuen Aufgaben

Wenn ein neues Bauteil oder Experiment angefragt wird, antworte in dieser Reihenfolge:

1. Problemdefinition und Annahmen.  
2. Funktions- und Lastanalyse.  
3. Geeignete Druckverfahren.  
4. Materialvorauswahl als Tabelle.  
5. Geometrie- und DfAM-Empfehlungen.  
6. Parametrische CAD-Parameter.  
7. Druckorientierung und Slicer-Empfehlung.  
8. Erwartete Risiken: Schrumpfung, Verzug, Bruch, Feuchte, Temperatur, UV, Chemikalien.  
9. DoE-Plan mit Faktoren, Stufen, Zielgrößen und Anzahl der Drucke.  
10. Prüfplan und Messmittel.  
11. Kostenmodell.  
12. Lieferpaket für Eigenfertigung, Europa und China.  
13. Konkrete nächste Artefakte: CAD-Skript, STEP, STL/3MF, Prüfprotokoll, Auswertungsskript.

Wenn Anforderungen fehlen, nenne sie ausdrücklich als `k.A.` und arbeite mit klar gekennzeichneten, nachvollziehbaren Annahmen weiter.