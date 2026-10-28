"""Gộp ``manifest.json`` của mọi thuật toán thành một bảng so sánh.

    python -m scripts.compare

Sinh ``output/so-sanh/diff.md``: mỗi đề một dòng, mỗi thuật toán một nhóm cột
(mở rộng / thời gian / kết quả), cộng cột cuối cho biết thuật toán nào nhanh
hơn trên đề đó.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def collect(output_dir: Path) -> dict[str, dict[str, dict]]:
    """algo -> kind -> tên đề -> mục manifest."""
    runs: dict[str, dict[str, dict]] = {}
    for manifest_path in sorted(output_dir.glob("*/*/*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        runs.setdefault(manifest["algo"], {})[manifest["kind"]] = manifest["results"]
    return runs


def _size(data_dir: Path, kind: str, name: str) -> str:
    path = data_dir / kind / f"{name}.json"
    if not path.exists():
        return "-"
    data = json.loads(path.read_text(encoding="utf-8"))
    return f"{data['rows']}x{data['cols']}"


def _faster(entries: dict[str, dict]) -> str:
    """Thuật toán nhanh nhất trong số những cái giải được.

    So theo độ chính xác hiển thị (0.01s) để cột này khớp với cột thời gian.
    """
    solved = {
        algo: round(entry["time_s"], 2)
        for algo, entry in entries.items()
        if entry["status"] == "xong"
    }
    if not solved:
        return "-"
    best = min(solved.values())
    winners = sorted(algo for algo, seconds in solved.items() if seconds == best)
    return "hoa" if len(winners) > 1 else winners[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="So sanh cac thuat toan")
    parser.add_argument("--data", type=Path, default=ROOT / "data")
    parser.add_argument("--out", type=Path, default=ROOT / "output")
    parser.add_argument(
        "--destination", type=Path, default=ROOT / "output" / "so-sanh" / "diff.md"
    )
    args = parser.parse_args(argv)

    runs = collect(args.out)
    if not runs:
        print("chua co manifest.json nao -- chay scripts.run truoc")
        return 1

    algos = sorted(runs)
    puzzles = sorted(
        {(kind, name) for by_kind in runs.values() for kind, results in by_kind.items()
         for name in results}
    )

    header = ["De", "Kich thuoc"]
    divider = ["---", "---"]
    for algo in algos:
        header += [f"{algo}: mo rong", f"{algo}: thoi gian (s)", f"{algo}: ket qua"]
        divider += ["---:", "---:", "---"]
    header.append("Nhanh hon")
    divider.append("---")

    rows = ["| " + " | ".join(header) + " |", "|" + "|".join(divider) + "|"]
    for kind, name in puzzles:
        line = [f"| `{name}` | {_size(args.data, kind, name)} |"]
        entries = {}
        for algo in algos:
            entry = runs[algo].get(kind, {}).get(name)
            if entry is None:
                line.append(" - | - | - |")
                continue
            entries[algo] = entry
            expanded = "-" if entry["expanded"] < 0 else entry["expanded"]
            line.append(
                f" {expanded} | {entry['time_s']:.2f} | {entry['status']} |"
            )
        line.append(f" {_faster(entries)} |")
        rows.append("".join(line))

    total = len(puzzles)
    summary = ["", f"Tong: {total} de."]
    for algo in algos:
        solved = sum(
            1 for results in runs[algo].values() for entry in results.values()
            if entry["status"] == "xong"
        )
        summary.append(f"- `{algo}`: giai duoc {solved}/{total}.")

    destination = args.destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join([*rows, *summary]) + "\n", encoding="utf-8")
    print("\n".join(summary))
    print(f"-> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
