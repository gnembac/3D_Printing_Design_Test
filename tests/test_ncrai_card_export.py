from pathlib import Path

import pytest

EXPORTS = tuple(
    Path(__file__).resolve().parent.parent
    / "exports"
    / "3mf"
    / f"NCRAI-card_variant-{variant}_EXP_MJF_PAC-HP_2026-10-09.3mf"
    for variant in ("A", "A2")
)


@pytest.mark.parametrize("export", EXPORTS, ids=lambda p: p.name)
def test_card_3mf_passes_strict_lib3mf_read(export: Path) -> None:
    lib3mf = pytest.importorskip("lib3mf")
    if not export.exists():
        pytest.skip("export not present")
    wrapper = lib3mf.Wrapper()
    model = wrapper.CreateModel()
    reader = model.QueryReader("3mf")
    reader.SetStrictModeActive(True)
    reader.ReadFromFile(str(export))
    assert reader.GetWarningCount() == 0
    assert model.GetTexture2Ds().Count() == 1
    assert model.GetTexture2DGroups().Count() == 1
