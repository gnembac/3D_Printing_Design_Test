"""Public-repo hygiene check for tracked files (used by CI).

Fails if git tracks files that must never be committed (see .claude/CLAUDE.md
"GitHub repository conventions" and "Code quality") or binaries larger than
the size limit that belong in Git LFS.

Usage:
    python scripts/check_repo_hygiene.py
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_FILE_BYTES = 10 * 1024 * 1024
FORBIDDEN_PATTERNS = (
    ".env",
    ".env.*",
    "secrets/*",
    "*.pem",
    "*.key",
    "id_rsa*",
    ".claude/settings.local.json",
)


def is_forbidden(relative_path: str) -> bool:
    path = PurePosixPath(relative_path)
    return (
        any(
            fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(relative_path, pattern)
            for pattern in FORBIDDEN_PATTERNS
        )
        or "secrets" in path.parts[:-1]
    )


def tracked_files(repo_root: Path = REPO_ROOT) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=repo_root, capture_output=True, check=True
    )
    return [name for name in result.stdout.decode().split("\0") if name]


def find_problems(files: list[str], repo_root: Path = REPO_ROOT) -> list[str]:
    problems: list[str] = []
    for name in files:
        if is_forbidden(name):
            problems.append(f"{name}: must not be committed")
        path = repo_root / name
        if path.is_file() and path.stat().st_size > MAX_FILE_BYTES:
            problems.append(
                f"{name}: larger than {MAX_FILE_BYTES // 1024 // 1024} MB - use Git LFS"
            )
    return problems


def main() -> int:
    problems = find_problems(tracked_files())
    if problems:
        print("Repo hygiene check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("Repo hygiene check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
