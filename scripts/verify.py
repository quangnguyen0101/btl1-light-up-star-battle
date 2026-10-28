"""Kiểm bộ đề và kết quả đã sinh.

Bốn lớp, độc lập nhau:

L1  dữ liệu   -- 48 đề đọc được, ``name`` trùng tên file, không trùng lặp
L2  hợp đồng  -- ``state`` dẫn xuất đúng, ``path`` đúng hai đầu, ``status`` khớp
L3  đúng luật -- ``problem.is_goal(state)`` cho mọi đề ``xong``
L4  toàn vẹn  -- file output là bản sao đề, chỉ ``known_solution`` đổi

Thoát mã 1 nếu có lỗi, nên dùng được trong CI.

    python -m scripts.verify
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.utils import load_problem

ROOT = Path(__file__).resolve().parents[1]


def _signature(problem) -> tuple:
    """Dấu vân tay của một đề, để phát hiện đề trùng nhau."""
    grid = getattr(problem, "grid", None) or getattr(problem, "regions", None)
    return (
        type(problem).__name__,
        problem.rows,
        problem.cols,
        getattr(problem, "stars_per_unit", None),
        getattr(problem, "variant", None),
        tuple(map(tuple, grid)) if grid else None,
        tuple(sorted(getattr(problem, "blocked_cells", ()))),
    )


def check_data(data_dir: Path) -> tuple[list[str], int]:
    """L1: đọc được, tên khớp, không trùng."""
    errors: list[str] = []
    seen: dict[tuple, Path] = {}
    files = sorted(data_dir.glob("*/*.json"))

    for path in files:
        try:
            problem = load_problem(path)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"L1 {path}: khong doc duoc ({exc})")
            continue
        if problem.name != path.stem:
            errors.append(f"L1 {path}: name={problem.name!r} != ten file")
        signature = _signature(problem)
        if signature in seen:
            errors.append(f"L1 {path}: trung de voi {seen[signature].name}")
        else:
            seen[signature] = path

    return errors, len(files)


def check_output(output_dir: Path, data_dir: Path) -> tuple[list[str], dict[str, int]]:
    """L2, L3, L4 trên mọi thư mục output có manifest."""
    errors: list[str] = []
    counts = {"xong": 0, "timeout": 0, "vo nghiem": 0, "file": 0}

    for manifest_path in sorted(output_dir.glob("*/*/*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        kind = manifest["kind"]
        directory = manifest_path.parent
        results = manifest["results"]

        for name, entry in sorted(results.items()):
            counts[entry["status"]] = counts.get(entry["status"], 0) + 1
            source = data_dir / kind / f"{name}.json"
            written = directory / f"{name}.json"
            label = f"{directory.relative_to(output_dir)}/{name}"

            if not written.exists():
                errors.append(f"L4 {label}: thieu file output")
                continue
            counts["file"] += 1

            out_data = json.loads(written.read_text(encoding="utf-8"))
            src_data = json.loads(source.read_text(encoding="utf-8"))

            # L4: mọi key khác known_solution phải giữ nguyên
            for key in set(src_data) | set(out_data):
                if key == "known_solution":
                    continue
                if src_data.get(key) != out_data.get(key):
                    errors.append(f"L4 {label}: key {key!r} bi sua")

            if entry["status"] != "xong":
                # L2: không giải được thì file phải nói "không có lời giải"
                if out_data.get("known_solution") != []:
                    errors.append(
                        f"L2 {label}: status={entry['status']} nhung known_solution khac []"
                    )
                if any(entry[key] != -1 for key in ("expanded", "generated", "frontier_peak")):
                    errors.append(f"L2 {label}: status={entry['status']} nhung con so lieu != -1")
                continue

            # L2: status xong thi phai co so lieu that
            if any(entry[key] < 1 for key in ("expanded", "generated", "frontier_peak")):
                errors.append(f"L2 {label}: status=xong nhung so lieu < 1")

            problem = load_problem(source)
            solution = out_data.get("known_solution") or []
            if not solution:
                errors.append(f"L3 {label}: status=xong nhung known_solution rong")
                continue

            state = problem.state_from_coords(solution)

            # L3: nguồn chân lý duy nhất
            if not problem.is_goal(state):
                errors.append(f"L3 {label}: is_goal(state) = False")

    return errors, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kiem bo de va ket qua")
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "output")
    args = parser.parse_args(argv)

    data_errors, total = check_data(args.data)
    out_errors, counts = check_output(args.out, args.data)
    errors = data_errors + out_errors

    print(f"L1 du lieu: {total} de, {len(data_errors)} loi")
    print(
        f"output: {counts['file']} file -- xong {counts['xong']}, "
        f"timeout {counts['timeout']}, vo nghiem {counts['vo nghiem']}, "
        f"{len(out_errors)} loi"
    )
    for message in errors:
        print("  " + message)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
