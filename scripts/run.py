"""Chạy một thuật toán trên cả bộ đề.

    python -m scripts.run --algo dfs
    python -m scripts.run --algo a_star --kind light_up --timeout 30

Kết quả ghi vào ``output/<họ>/<algo>/<kind>/``: bản sao đề (chỉ thay
``known_solution``), ``bang.md`` (7 cột cho người đọc) và ``manifest.json``
(số liệu cho ``scripts/verify.py`` và ``scripts/compare.py``).
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from src.registry import ALGORITHMS
from src.utils import (
    Timeout,
    load_problem,
    manifest_entry,
    table_row,
    timeout as time_limit,
    write_output,
    write_table,
)

ROOT = Path(__file__).resolve().parents[1]


def _jobs(data_dir: Path, kind: str | None):
    """Các cặp (problem, đường dẫn) cần chạy, xếp theo kích thước rồi tên."""
    jobs = []
    for path in sorted(data_dir.glob("*/*.json")):
        problem = load_problem(path)
        if kind is not None and path.parent.name != kind:
            continue
        jobs.append((problem, path))
    jobs.sort(key=lambda job: (job[0].rows * job[0].cols, job[1].stem))
    return jobs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Chay mot thuat toan tren bo de")
    parser.add_argument("--algo", required=True, choices=sorted(ALGORITHMS))
    parser.add_argument("--kind", choices=("star_battle", "light_up"))
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "output")
    args = parser.parse_args(argv)

    family, algorithm = ALGORITHMS[args.algo]
    out_root = args.out / family / args.algo

    rows: dict[str, list[str]] = {}
    results: dict[str, dict[str, dict]] = {}

    for problem, path in _jobs(args.data, args.kind):
        kind = path.parent.name
        started = time.perf_counter()
        try:
            with time_limit(args.timeout):
                result = algorithm(problem)
        except Timeout:
            result = None
        elapsed = time.perf_counter() - started

        if result is None:
            status, expanded, generated, peak = "timeout", -1, -1, -1
            solution = []
        else:
            status = "xong" if result["solution"] else "vo nghiem"
            expanded = result["expanded"]
            generated = result["generated"]
            peak = result["frontier_peak"]
            solution = result["solution"]

        write_output(path, out_root / kind / path.name, solution)

        size = f"{problem.rows}x{problem.cols}"
        rows.setdefault(kind, []).append(
            table_row(path.stem, size, expanded, elapsed, status, generated, peak)
        )
        results.setdefault(kind, {})[path.stem] = manifest_entry(
            status, expanded, generated, peak, elapsed
        )
        print(f"{kind}/{path.stem}: {status} ({elapsed:.2f}s)", flush=True)

    for kind, kind_rows in rows.items():
        directory = out_root / kind
        write_table(directory / "bang.md", kind_rows)
        manifest = {
            "algo": args.algo,
            "kind": kind,
            "timeout": args.timeout,
            "chay_luc": datetime.now().isoformat(timespec="seconds"),
            "results": results[kind],
        }
        (directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"-> {directory}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
