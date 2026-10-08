import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_repo_hygiene import find_problems, is_forbidden  # noqa: E402


def test_forbidden_files_detected() -> None:
    assert is_forbidden(".env")
    assert is_forbidden("config/.env.local")
    assert is_forbidden("secrets/token.txt")
    assert is_forbidden("keys/server.pem")
    assert is_forbidden(".claude/settings.local.json")


def test_regular_files_allowed() -> None:
    assert not is_forbidden("scripts/supplier_dfm_check.py")
    assert not is_forbidden("docs/reference/README.md")
    assert not is_forbidden(".claude/settings.json")


def test_oversized_file_reported(tmp_path: Path) -> None:
    big = tmp_path / "scan.stl"
    big.write_bytes(b"\0" * (10 * 1024 * 1024 + 1))
    (tmp_path / "small.txt").write_text("ok")
    problems = find_problems(["scan.stl", "small.txt"], repo_root=tmp_path)
    assert len(problems) == 1
    assert "Git LFS" in problems[0]
