"""Sinh toàn bộ ảnh trong ``figs/`` từ ``data/`` và ``output/``.

    python -m scripts.figures

- mỗi đề trong ``data/<kind>/`` -> ``figs/de/<kind>/<tên>.png``
- mỗi kết quả có lời giải trong ``output/<họ>/<algo>/<kind>/`` ->
  ``figs/<họ>/<algo>/<kind>/<tên>.png``

Đề không giải được (``known_solution: []``) thì bỏ qua, vì không có gì để vẽ thêm.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.utils import load_problem
from viz.core import save

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sinh anh cho de va loi giai")
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "output")
    parser.add_argument("--figs", type=Path, default=ROOT / "figs")
    parser.add_argument("--cell", type=int, default=46)
    args = parser.parse_args(argv)

    puzzles = 0
    for path in sorted(args.data.glob("*/*.json")):
        problem = load_problem(path)
        save(problem, None, args.figs / "de" / path.parent.name / f"{path.stem}.png",
             cell=args.cell)
        puzzles += 1

    solutions = 0
    for path in sorted(args.out.glob("*/*/*/*.json")):
        if path.name == "manifest.json":
            continue
        family, algo, kind, _ = path.relative_to(args.out).parts
        problem = load_problem(path)
        if not problem.known_solution:
            continue
        state = problem.state_from_coords(problem.known_solution)
        save(problem, state, args.figs / family / algo / kind / f"{path.stem}.png",
             cell=args.cell)
        solutions += 1

    print(f"de bai: {puzzles} anh | loi giai: {solutions} anh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
