from pathlib import Path

import pytest

EXPORT = (
    Path(__file__).resolve().parent.parent
    / "exports"
    / "3mf"
    / "NCRAI-card_variant-A_EXP_MJF_PAC-HP_2026-10-09.3mf"
)


def test_card_3mf_passes_strict_lib3mf_read() -> None:
    lib3mf = pytest.importorskip("lib3mf")
    if not EXPORT.exists():
        pytest.skip("export not present")
    wrapper = lib3mf.Wrapper()
    model = wrapper.CreateModel()
    reader = model.QueryReader("3mf")
    reader.SetStrictModeActive(True)
    reader.ReadFromFile(str(EXPORT))
    assert reader.GetWarningCount() == 0
    assert model.GetTexture2Ds().Count() == 1
    assert model.GetTexture2DGroups().Count() == 1
