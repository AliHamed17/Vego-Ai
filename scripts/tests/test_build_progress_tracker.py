from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = ROOT / "scripts/build-progress-tracker.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_progress_tracker", BUILDER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_recent_activity_returns_latest_entries_newest_first(tmp_path: Path) -> None:
    log = tmp_path / "session-log.md"
    log.write_text(
        "# Session Log\n\n"
        + "\n\n".join(f"## 2026-07-{day:02d} - Entry {day}" for day in range(1, 9))
        + "\n",
        encoding="utf-8",
    )
    builder = load_builder()
    assert builder.recent_activity_lines(log) == [
        "- 2026-07-08 - Entry 8",
        "- 2026-07-07 - Entry 7",
        "- 2026-07-06 - Entry 6",
        "- 2026-07-05 - Entry 5",
        "- 2026-07-04 - Entry 4",
        "- 2026-07-03 - Entry 3",
    ]
