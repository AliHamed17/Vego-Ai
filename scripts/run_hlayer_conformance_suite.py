"""Run and transactionally promote the EXP-013 through EXP-018 suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hlayer_offline.suite import execute_suite


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        help="Combined generated bundle directory (default: reports/generated/hlayer_conformance)",
    )
    args = parser.parse_args()
    manifest = execute_suite(args.output)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
