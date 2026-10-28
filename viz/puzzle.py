"""Vẽ đề bài (không có lời giải).

    python -m viz.puzzle data/star_battle/sb-5x5-normal-01.json
    python -m viz.puzzle data/light_up/lu-7x7-normal-01.json -o figs/de/light_up

Mặc định ảnh ra ``figs/de/<kind>/<tên đề>.png``.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.utils import load_problem
from viz.core import save

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ve de bai ra PNG")
    parser.add_argument("puzzle", type=Path)
    parser.add_argument("-o", "--out-dir", type=Path)
    parser.add_argument("--cell", type=int, default=46, help="kich thuoc o (px)")
    args = parser.parse_args(argv)

    problem = load_problem(args.puzzle)
    out_dir = args.out_dir or ROOT / "figs" / "de" / args.puzzle.parent.name
    path = save(problem, None, out_dir / f"{args.puzzle.stem}.png", cell=args.cell)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
