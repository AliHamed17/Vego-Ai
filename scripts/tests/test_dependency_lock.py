from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_dependency_lock.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_dependency_lock", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_requirement_projections_are_current() -> None:
    module = load_module()
    for path, content in module.expected().items():
        assert path.read_text(encoding="utf-8") == content
    module.validate_node_lock()
