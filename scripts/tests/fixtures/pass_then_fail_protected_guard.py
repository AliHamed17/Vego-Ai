"""Test fixture: pass once, then fail the pre-promotion boundary check."""

from __future__ import annotations

import os
from pathlib import Path

counter_path = Path(os.environ["HLAYER_TEST_GUARD_COUNTER"])
count = int(counter_path.read_text(encoding="utf-8")) if counter_path.is_file() else 0
counter_path.write_text(str(count + 1), encoding="utf-8")
raise SystemExit(0 if count == 0 else 9)
