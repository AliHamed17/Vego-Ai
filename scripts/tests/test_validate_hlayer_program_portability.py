from __future__ import annotations

import subprocess
from pathlib import Path

from validate_hlayer_program import (
    resolve_protected_change_base,
    validate_protected_paths,
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_protected_change_base_falls_back_to_local_main(tmp_path: Path, monkeypatch) -> None:
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.name", "Fixture")
    _git(tmp_path, "config", "user.email", "fixture@example.invalid")
    (tmp_path / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "fixture")
    monkeypatch.delenv("PR_BASE_SHA", raising=False)
    monkeypatch.delenv("H_LAYER_CHANGE_BASE", raising=False)
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)
    assert resolve_protected_change_base(tmp_path) == "main"


def test_missing_git_metadata_returns_structured_failure(tmp_path: Path) -> None:
    result = validate_protected_paths(tmp_path)
    assert result["status"] == "FAIL"
    assert result["base"] is None
    assert result["failures"]
