#!/usr/bin/env python3
"""Clean result.md by removing daily/weekly/monthly test entries.

This script scans result.md in the tong-hop repo and removes any lines
that refer to daily/weekly/monthly test variants (case-insensitive).
"""
from __future__ import annotations

from pathlib import Path
import re


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    target = root / "result.md"
    if not target.exists():
        print(f"No result.md found at {target}")
        return 1

    content = target.read_text(encoding="utf-8").splitlines()
    cleaned = []
    # remove any line mentioning daily/weekly/monthly (case-insensitive)
    for line in content:
        if re.search(r"daily|weekly|monthly", line, flags=re.IGNORECASE):
            continue
        cleaned.append(line)

    target.write_text("\n".join(cleaned) + "\n", encoding="utf-8")
    print(f"Cleaned {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
