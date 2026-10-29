"""Greedy Best-First cho Star Battle.

Cùng cách sinh nút với A* (``a_star/star_battle.py``): mỗi bước đặt đủ
``stars_per_unit`` sao cho hàng còn thiếu đầu tiên.

Khác A* ở thứ tự mở rộng: chỉ dùng ``h(n)``, không cộng chi phí ``g(n)``.
``h(n)`` đếm số cột và số vùng còn thiếu sao. Tổng số sao còn thiếu thì luôn
bằng nhau ở mọi độ sâu nên không phân biệt được hai nút; hai đại lượng này thì
giảm đúng khi đặt sao vào cột/vùng còn thiếu.

    from src.model.star_battle import StarBattleProblem
    from src.heuristic.greedy.star_battle import greedy

    problem = StarBattleProblem.from_json("data/star_battle/sb-5x5-normal-01.json")
    result = greedy(problem)
"""
from __future__ import annotations

import heapq

from src.heuristic.a_star.star_battle import _candidates
from src.model.result import build_result, path_from_came_from
from src.model.star_battle import StarBattleProblem


def _h(problem: StarBattleProblem, state: tuple[int, ...]) -> int:
    """Số cột và số vùng còn thiếu sao (0 khi mọi đơn vị đã đủ)."""
    k = problem.stars_per_unit
    short = 0
    for c in range(problem.cols):
        if sum((mask >> c) & 1 for mask in state) < k:
            short += 1

    if problem.regions is not None:
        count: dict[object, int] = {}
        for r, mask in enumerate(state):
            for c in range(problem.cols):
                if (mask >> c) & 1:
                    rid = problem.regions[r][c]
                    count[rid] = count.get(rid, 0) + 1
        for rid in {x for row in problem.regions for x in row}:
            if count.get(rid, 0) < k:
                short += 1

    return short


def greedy(problem: StarBattleProblem) -> dict:
    """Greedy Best-First trên Star Battle, trả về hợp đồng kết quả chung."""
    rows, k = problem.rows, problem.stars_per_unit
    start: tuple[int, ...] = tuple([0] * rows)

    counter = 0
    heap = [(_h(problem, start), counter, start)]
    came_from: dict[tuple[int, ...], tuple[int, ...] | None] = {start: None}
    expanded = 0
    generated = 1
    peak = 1

    while heap:
        _, _, state = heapq.heappop(heap)
        expanded += 1  # mọi nút pop đều tính, kể cả nút goal

        row = next((r for r in range(rows) if state[r].bit_count() < k), None)
        if row is None:
            if problem.is_goal(state):
                return build_result(
                    problem,
                    solution=problem.coords_from_state(state),
                    path=path_from_came_from(came_from, state, start),
                    expanded=expanded,
                    generated=generated,
                    frontier_peak=peak,
                )
            continue

        for _, mask in _candidates(problem, state, row):
            nxt = state[:row] + (state[row] | mask,) + state[row + 1:]
            if nxt in came_from:
                continue
            if not problem.is_valid_state(nxt, partial=True):
                continue
            came_from[nxt] = state
            generated += 1
            counter += 1
            heapq.heappush(heap, (_h(problem, nxt), counter, nxt))
            peak = max(peak, len(heap))

    return build_result(
        problem,
        expanded=expanded,
        generated=generated,
        frontier_peak=peak,
    )
