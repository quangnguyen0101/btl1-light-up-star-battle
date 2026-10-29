"""Greedy Best-First cho Light Up (có lan truyền ràng buộc).

Dùng lại ``_segments``, ``_free_choices`` và ``_propagate`` của A*
(``a_star/light_up.py``) nên các bước bắt buộc và cách chọn ô (MRV) giống hệt.

Khác A* ở thứ tự mở rộng: chỉ dùng ``h(n)``, không cộng chi phí ``g(n)``.
``h(n)`` là số ô trắng còn chưa được chiếu sáng. Mỗi bóng đèn làm giảm đúng
số ô này, nên nút nào chiếu sáng được nhiều ô hơn sẽ được mở rộng trước.

Vì gốc là trạng thái sau lan truyền, ``path`` được bổ sung bàn cờ trống ở đầu
để ``path[0]`` luôn là bàn cờ chưa đặt gì.

    from src.model.light_up import LightUpProblem
    from src.heuristic.greedy.light_up import greedy

    problem = LightUpProblem.from_json("data/light_up/lu-7x7-normal-01.json")
    result = greedy(problem)
"""
from __future__ import annotations

import heapq

from src.heuristic.a_star.light_up import (
    _free_choices,
    _place,
    _propagate,
    _segments,
)
from src.model.light_up import LightUpProblem
from src.model.result import build_result, path_from_came_from


def greedy(problem: LightUpProblem) -> dict:
    """Greedy Best-First trên Light Up, trả về hợp đồng kết quả chung."""
    whites = {
        (r, c)
        for r in range(problem.rows)
        for c in range(problem.cols)
        if problem.grid[r][c] == "."
    }
    segments = _segments(problem)

    empty: tuple[int, ...] = tuple([0] * problem.rows)
    start, ok = _propagate(problem, segments, whites, empty)
    if not ok:
        return build_result(problem, expanded=0, generated=0, frontier_peak=0)

    def h_of(state):
        return len(whites - problem.illuminated_cells(state))

    counter = 0
    heap = [(h_of(start), counter, start)]
    came_from: dict[tuple[int, ...], tuple[int, ...] | None] = {start: None}
    expanded = 0
    generated = 1
    peak = 1

    while heap:
        _, _, state = heapq.heappop(heap)
        expanded += 1  # mọi nút pop đều tính, kể cả nút goal

        unlit = whites - problem.illuminated_cells(state)
        if not unlit:
            if problem.is_goal(state):
                return build_result(
                    problem,
                    solution=problem.coords_from_state(state),
                    path=path_from_came_from(came_from, state, empty),
                    expanded=expanded,
                    generated=generated,
                    frontier_peak=peak,
                )
            continue

        # MRV: ưu tiên ô chưa sáng có ít lựa chọn nhất.
        _, choices = min(
            ((cell, _free_choices(problem, segments, state, cell)) for cell in unlit),
            key=lambda x: len(x[1]),
        )

        for r, c in choices:
            nxt, ok = _propagate(problem, segments, whites, _place(state, r, c))
            if not ok or nxt in came_from:
                continue
            came_from[nxt] = state
            generated += 1
            counter += 1
            heapq.heappush(heap, (h_of(nxt), counter, nxt))
            peak = max(peak, len(heap))

    return build_result(
        problem,
        expanded=expanded,
        generated=generated,
        frontier_peak=peak,
    )
