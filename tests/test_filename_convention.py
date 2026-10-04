import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from filename_convention import is_valid_filename, parse_filename  # noqa: E402


def test_parses_valid_filename() -> None:
    parsed = parse_filename("DOE003_warping-coupon_R02_FDM_ASA_2026-10-04.step")
    assert parsed is not None
    assert parsed.project == "DOE003"
    assert parsed.part_number == "warping-coupon"
    assert parsed.revision == "R02"
    assert parsed.process == "FDM"
    assert parsed.material == "ASA"
    assert parsed.date == "2026-10-04"
    assert parsed.extension == "step"


def test_accepts_exp_and_rel_revisions() -> None:
    assert is_valid_filename("EX001_calib-cube_EXP_FDM_PLA_2026-10-04.stl")
    assert is_valid_filename("DOE004_tensile-bar_REL_FDM_PETG_2026-10-04.3mf")


def test_rejects_missing_revision() -> None:
    assert not is_valid_filename("DOE003_warping-coupon_FDM_ASA_2026-10-04.step")


def test_rejects_wrong_date_format() -> None:
    assert not is_valid_filename("DOE003_warping-coupon_R02_FDM_ASA_04-10-2026.step")


def test_rejects_unknown_extension_separator() -> None:
    assert parse_filename("not_a_valid_filename") is None
