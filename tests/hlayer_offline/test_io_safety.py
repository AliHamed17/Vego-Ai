from __future__ import annotations

from pathlib import Path

import pytest

from vego_hlayer.contracts import ValidationError
from vego_hlayer.io_safety import validate_input_file, validate_output_file


def test_output_rejects_protected_and_outside_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "reports" / "generated").mkdir(parents=True)
    (repo / "VEGO-AI" / "eval_output").mkdir(parents=True)
    with pytest.raises(ValidationError, match="eval_output"):
        validate_output_file(
            repo / "VEGO-AI" / "eval_output" / "result.json",
            repo_root=repo,
        )
    with pytest.raises(ValidationError, match="approved output roots"):
        validate_output_file(
            repo / "unapproved.json",
            repo_root=repo,
            allowed_roots=(repo / "reports" / "generated",),
        )


def test_output_rejects_overwrite(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output = repo / "reports" / "generated" / "result.json"
    output.parent.mkdir(parents=True)
    output.write_text("existing", encoding="utf-8")
    with pytest.raises(ValidationError, match="overwrite"):
        validate_output_file(output, repo_root=repo)


def test_input_rejects_oversized_file(tmp_path: Path) -> None:
    path = tmp_path / "input.json"
    path.write_bytes(b"1234")
    with pytest.raises(ValidationError, match="exceeds"):
        validate_input_file(path, max_bytes=3)
