"""Bảng Markdown và manifest của một lượt chạy."""
from __future__ import annotations

from pathlib import Path

#: Bảy cột, theo bảng của bản DFS (V2).
TABLE_HEADER = (
    "| De | Kich thuoc | Mo rong | Thoi gian (s) | Ket qua | Sinh ra | Stack max |",
    "|---|---|---:|---:|---|---:|---:|",
)

#: Ba giá trị ``status`` mà runner được phép đặt.
STATUSES = ("xong", "timeout", "vo nghiem")


def table_row(
    name: str,
    size: str,
    expanded: int,
    time_s: float,
    status: str,
    generated: int,
    frontier_peak: int,
) -> str:
    """Một dòng bảng số liệu."""
    return (
        f"| `{name}` | {size} | {expanded} | {time_s:.2f} | {status} "
        f"| {generated} | {frontier_peak} |"
    )


def write_table(path: str | Path, rows: list[str]) -> None:
    """Ghi ``bang.md`` từ danh sách dòng đã định dạng."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([*TABLE_HEADER, *rows]) + "\n", encoding="utf-8")


def manifest_entry(
    status: str,
    expanded: int,
    generated: int,
    frontier_peak: int,
    time_s: float,
) -> dict:
    """Một mục trong ``manifest.json`` (số liệu máy đọc, khác ``bang.md``)."""
    return {
        "status": status,
        "expanded": expanded,
        "generated": generated,
        "frontier_peak": frontier_peak,
        "time_s": round(time_s, 3),
    }
