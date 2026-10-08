# scripts

CAD generation, DoE design, analysis and cost-model scripts (Python 3.12, type-hinted, tested).

| Script | Purpose |
|---|---|
| `filename_convention.py` | parse/validate the project filename convention |
| `validate_cad_exports.py` | validate CAD exports before release |
| `generate_manifest.py` | generate the export manifest |
| `supplier_dfm_check.py` | DfM pre-check against Supplier CN-A published design rules |
| `check_repo_hygiene.py` | CI check: no secrets files tracked, no files > 10 MB (use Git LFS) |
