"""Vẽ bàn cờ bằng Pillow: đề bài (``state=None``) hoặc đề + lời giải.

Một ảnh duy nhất, giống các hình đang dùng trong báo cáo:

- **Star Battle**: mỗi vùng một màu (bước hue theo tỉ lệ vàng để hai vùng cạnh
  nhau luôn khác màu), ô bị khoá tô đen, mỗi ngôi sao là một ngôi sao 5 cánh.
- **Light Up**: tường và tường số tô xám, bóng đèn là hình tròn vàng, các ô
  đang được chiếu sáng tô nền vàng nhạt.
"""
from __future__ import annotations

import colorsys
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.model.light_up import LightUpProblem
from src.model.star_battle import StarBattleProblem

CELL = 46
GRID_LINE = "#888888"
WALL = "#333333"
BLOCKED = "#1a1a1a"
LIT = "#fff4c2"
BULB = "#f5c330"
BULB_EDGE = "#a07800"
STAR = "#1a1a1a"


def _palette(regions) -> dict:
    """Màu cho từng vùng; bước hue 0.618 giúp vùng kề nhau luôn tương phản."""
    ids = sorted({rid for row in regions for rid in row}, key=str)
    return {
        rid: tuple(int(255 * v) for v in colorsys.hsv_to_rgb(i * 0.618 % 1, 0.55, 0.98))
        for i, rid in enumerate(ids)
    }


def _star_points(cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    """Năm đỉnh ngoài và năm đỉnh trong của ngôi sao 5 cánh."""
    points = []
    for index in range(10):
        angle = -math.pi / 2 + index * math.pi / 5
        r = radius if index % 2 == 0 else radius * 0.45
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points


def _draw_star_battle(draw, problem, state, cell, show_regions: bool) -> None:
    regions = problem.regions if show_regions else None
    palette = _palette(problem.regions) if regions else {}

    for r in range(problem.rows):
        for c in range(problem.cols):
            x, y = c * cell + 1, r * cell + 1
            box = (x, y, x + cell, y + cell)
            mid = (x + cell / 2, y + cell / 2)

            if regions:
                fill = palette[problem.regions[r][c]]
            elif (r, c) in problem.blocked_cells:
                fill = BLOCKED
            else:
                fill = "white"
            draw.rectangle(box, fill=fill, outline=GRID_LINE, width=1)

            if state[r] >> c & 1:
                draw.polygon(
                    _star_points(mid[0], mid[1], cell * 0.32), fill=STAR
                )


def _draw_light_up(draw, problem, state, cell, font) -> None:
    lit = problem.illuminated_cells(state)

    for r in range(problem.rows):
        for c in range(problem.cols):
            x, y = c * cell + 1, r * cell + 1
            box = (x, y, x + cell, y + cell)
            mid = (x + cell / 2, y + cell / 2)
            kind = problem.grid[r][c]

            if kind == ".":
                fill = LIT if (r, c) in lit else "white"
            else:
                fill = WALL
            draw.rectangle(box, fill=fill, outline=GRID_LINE, width=1)

            if kind in "01234":
                draw.text(mid, kind, fill="white", font=font, anchor="mm")

            if state[r] >> c & 1:
                radius = cell * 0.3
                draw.ellipse(
                    (mid[0] - radius, mid[1] - radius, mid[0] + radius, mid[1] + radius),
                    fill=BULB,
                    outline=BULB_EDGE,
                    width=1,
                )


def draw(problem, state=None, *, cell: int = CELL, show_regions: bool = True) -> Image.Image:
    """Vẽ bàn cờ thành ``PIL.Image``.

    ``state=None`` vẽ đề bài; truyền ``state`` (tuple bitmask) để vẽ kèm lời giải.
    """
    if state is None:
        state = tuple([0] * problem.rows)

    image = Image.new(
        "RGB", (problem.cols * cell + 2, problem.rows * cell + 2), "white"
    )
    painter = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=max(8, int(cell * 0.55)))

    if isinstance(problem, StarBattleProblem):
        _draw_star_battle(painter, problem, state, cell, show_regions)
    elif isinstance(problem, LightUpProblem):
        _draw_light_up(painter, problem, state, cell, font)
    else:
        raise TypeError(f"khong ve duoc loai bai: {type(problem).__name__}")

    return image


def save(problem, state, path: str | Path, **kwargs) -> Path:
    """Vẽ và ghi ra ``path`` (thư mục cha được tạo nếu chưa có)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    draw(problem, state, **kwargs).save(path)
    return path
