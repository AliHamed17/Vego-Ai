"""Read-only CLI validator for EXP-013 through EXP-018 and their contracts."""

from __future__ import annotations

import json

from hlayer_offline.validator import validate


def main() -> int:
    result = validate()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
