"""Vẽ đề + lời giải từ một file trong ``output/``.

    python -m viz.solution output/heuristic/a_star/star_battle/sb-5x5-normal-01.json

Mặc định ảnh ra ``figs/<họ>/<algo>/<kind>/<tên đề>.png``, lấy đúng đường dẫn
của file output.  Đề không có lời giải (``known_solution: []``) thì báo lỗi,
vì không có gì để vẽ thêm.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.utils import load_problem
from viz.core import save

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ve de + loi giai ra PNG")
    parser.add_argument("file", type=Path, help="file JSON trong output/")
    parser.add_argument("-o", "--out-dir", type=Path)
    parser.add_argument("--cell", type=int, default=46, help="kich thuoc o (px)")
    args = parser.parse_args(argv)

    problem = load_problem(args.file)
    if not problem.known_solution:
        print(f"{args.file}: khong co loi giai de ve")
        return 1

    if args.out_dir is not None:
        out_dir = args.out_dir
    else:
        parts = args.file.resolve().parts
        try:
            anchor = parts.index("output")
            family, algo, kind = parts[anchor + 1:anchor + 4]
        except ValueError:
            print("khong suy ra duoc thu muc figs -- hay truyen -o")
            return 1
        out_dir = ROOT / "figs" / family / algo / kind

    state = problem.state_from_coords(problem.known_solution)
    path = save(problem, state, out_dir / f"{args.file.stem}.png", cell=args.cell)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
