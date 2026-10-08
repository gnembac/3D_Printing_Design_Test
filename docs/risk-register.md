# Risk Register

| # | Risk | Area | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|---|
| 1 | Mechanical property claimed without stating orientation/method | Documentation | medium | high | Enforce `CLAUDE.md` "Mandatory working principles" | open |
| 2 | Safety-critical part designed without validation plan | Safety | low | high | Enforce `CLAUDE.md` "Safety and scope" | open |
| 3 | Supplier changes material/process without written approval | Supply chain | medium | high | Change-control clause, see `docs/manufacturing-guidelines-eu-china.md` | open |
| 4 | Sensitive supplier/pricing data committed to public repo | Repository | medium | medium | Enforce `CLAUDE.md` "GitHub repository conventions" | open |
| 5 | Supplier datasheet values (wrong units, shifted tables, mixed HDT loads/standards) used as design values | Data quality | high | medium | `quality_flag` in `data/material-datasheets/jlc3dp/`; rules in `CLAUDE.md` "External manufacturing reference data" | open |
| 6 | Outsourced part fails due to stale website rules/prices | Supply chain | medium | medium | Re-verify before RFQ; dated re-check files | open |
| 7 | Untraceable material (e.g. JLC3DP "X Resin") used in experiment | Traceability | low | high | Excluded by `CLAUDE.md` rule | open |
