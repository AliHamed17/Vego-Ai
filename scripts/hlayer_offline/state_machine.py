"""Compatibility re-export for the canonical H-layer state machine."""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from vego_hlayer.state_machine import *  # noqa: F401,F403,E402
