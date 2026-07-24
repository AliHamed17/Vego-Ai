"""CLI for the isolated EXP-015 workload, bundling, and fairness experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from hlayer_offline.exp015 import execute


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, help="Generated output directory (default: reports/generated/exp015)"
    )
    args = parser.parse_args()
    return 0 if execute(args.output)["summary"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
