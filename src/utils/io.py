"""Đọc file đề và ghi file kết quả, giữ nguyên định dạng JSON của repo."""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.model.light_up import LightUpProblem
from src.model.star_battle import StarBattleProblem

PROBLEM_TYPES = {
    "light_up": LightUpProblem,
    "star_battle": StarBattleProblem,
}


def problem_from_dict(data: dict):
    """Chọn lớp model theo trường ``type`` của file JSON."""
    kind = data.get("type")
    if kind not in PROBLEM_TYPES:
        raise ValueError(
            f"type khong ho tro: {kind!r}; chi nhan {sorted(PROBLEM_TYPES)}"
        )
    return PROBLEM_TYPES[kind].from_dict(data)


def load_problem(path: str | Path):
    """Đọc một file đề JSON thành đối tượng model."""
    return problem_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def dump_json(data: dict) -> str:
    """``json.dumps(indent=2)`` nhưng mảng trong cùng nằm trên một dòng.

    Nhờ vậy ``grid``/``regions``/``known_solution`` đọc được bằng mắt, giống
    các file trong ``data/``.
    """
    text = json.dumps(data, indent=2, ensure_ascii=False)
    return re.sub(
        r"\[\s+([^\[\]]*?)\s+\]",
        lambda m: "[" + re.sub(r",\s+", ", ", m[1]) + "]",
        text,
    ) + "\n"


def write_output(source: str | Path, destination: str | Path, solution) -> None:
    """Ghi bản sao của đề, chỉ thay ``known_solution`` bằng ``solution``.

    ``solution`` là danh sách toạ độ ``[[r, c], ...]``; khi không giải được
    truyền ``[]`` để file tự nói "không có lời giải".
    """
    data = json.loads(Path(source).read_text(encoding="utf-8"))
    data["known_solution"] = [[int(r), int(c)] for r, c in solution]

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(dump_json(data), encoding="utf-8")
