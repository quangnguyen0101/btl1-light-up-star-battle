"""Chạy một đề và in tiến trình theo từng bước của ``path``.

    python -m scripts.demo --algo dfs --puzzle data/star_battle/sb-5x5-normal-01.json
    python -m scripts.demo --algo greedy --puzzle data/light_up/lu-7x7-normal-01.json --timeout 10

``path[0]`` là bàn cờ trống, ``path[-1]`` là lời giải.  Với Greedy Light Up, các
bước đầu có thể nhảy nhiều bóng một lúc: đó là các bước bắt buộc do lan truyền
ràng buộc, không phải quyết định của thuật toán.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from src.registry import ALGORITHMS
from src.utils import Timeout, load_problem, timeout as time_limit

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chay mot de va in tien trinh")
    parser.add_argument("--algo", required=True, choices=sorted(ALGORITHMS))
    parser.add_argument("--puzzle", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--max-steps",
        type=int,
        default=0,
        help="chi in toi da bao nhieu buoc (0 = in het)",
    )
    args = parser.parse_args(argv)

    problem = load_problem(args.puzzle)
    _, algorithm = ALGORITHMS[args.algo]

    started = time.perf_counter()
    try:
        with time_limit(args.timeout):
            result = algorithm(problem)
    except Timeout:
        print(f"{problem.name}: timeout sau {args.timeout}s")
        return 1
    elapsed = time.perf_counter() - started

    print(
        f"{problem.name}: {problem.rows}x{problem.cols} -- {args.algo}, "
        f"mo rong={result['expanded']} sinh ra={result['generated']} "
        f"stack max={result['frontier_peak']} thoi gian={elapsed:.3f}s"
    )

    if not result["solution"]:
        print("khong tim thay loi giai")
        return 1

    path = result["path"]
    limit = len(path) if args.max_steps <= 0 else min(args.max_steps, len(path))
    for index in range(limit):
        print(f"\nbuoc {index}/{len(path) - 1}")
        print(problem.render(path[index]))

    if limit < len(path):
        print(f"\n... con {len(path) - limit} buoc")

    print(f"\nis_goal(path[-1]) = {problem.is_goal(result['state'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
