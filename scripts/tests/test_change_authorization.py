from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_hlayer_change_authorization.py"


def load_module():
    spec = importlib.util.spec_from_file_location("change_authorization", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_authorized_protected_content_is_hash_bound(tmp_path: Path) -> None:
    module = load_module()
    protected = tmp_path / "VEGO-AI" / "framework" / "llm_client.py"
    protected.parent.mkdir(parents=True)
    protected.write_text("baseline\n", encoding="utf-8")
    run_git(tmp_path, "init")
    run_git(tmp_path, "config", "user.email", "fixture@example.invalid")
    run_git(tmp_path, "config", "user.name", "Fixture")
    run_git(tmp_path, "add", "VEGO-AI/framework/llm_client.py")
    run_git(tmp_path, "commit", "-m", "baseline")

    protected.write_text("authorized hardening\n", encoding="utf-8")
    authorization = tmp_path / "authorization.json"
    config = {
        "allowed_paths": ["VEGO-AI/framework/llm_client.py"],
        "authorized_content_sha256": {
            "VEGO-AI/framework/llm_client.py": module._portable_sha256(protected)
        },
        "forbidden_paths": [],
        "merge_requires_independent_approval": True,
        "authorization_expires_on": "2099-12-31",
    }
    authorization.write_text(json.dumps(config), encoding="utf-8")
    assert module.inspect(tmp_path, authorization, "HEAD")["status"] == "PASS"

    protected.write_text("later unreviewed change\n", encoding="utf-8")
    result = module.inspect(tmp_path, authorization, "HEAD")
    assert result["status"] == "FAIL"
    assert any("content differs" in item for item in result["failures"])
