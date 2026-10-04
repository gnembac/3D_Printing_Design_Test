# Experiment Protocol

```text
Experiment-ID:             DOE-NNN-<slug>
Date:
Operator(s):
Printer(s):
Manufacturing process:
```

## 1. Hypothesis

State the hypothesis under test and why it matters.

## 2. Objective / response variables

| Response variable | Unit | Measurement method |
|---|---|---|
| | | |

## 3. Factors

| Factor | Symbol | Low level | High level | Unit | Source of range |
|---|---|---|---|---|---|
| | | | | | manufacturer data / literature / prior exercise |

## 4. Design

- DoE type (screening / full factorial / RSM / Taguchi / ...):
- Number of runs:
- Center points / repetitions:
- Randomization scheme:
- Blocking factors (printer, batch, date, operator):

## 5. Measurement plan

- Instruments and calibration status:
- Sample size per condition:
- Acceptance / rejection criteria for a run:

## 6. Material

- Manufacturer, product, batch/lot, color:
- Drying/storage condition:
- Reference to `data/material-datasheets/`:

## 7. Raw data

Link to `data/raw/<experiment-id>/...`. Never edit raw data in place.

## 8. Analysis

Link to analysis script/notebook in `scripts/` or `notebooks/`.
State assumptions checked before using ANOVA or other inferential statistics.

## 9. Limitations

State what this result does NOT prove (printer-specific, batch-specific,
sample-size limits, non-standard test method, etc.).

## 10. Conclusion and next experiment

Design rule derived, and the recommended follow-up experiment or exercise.
