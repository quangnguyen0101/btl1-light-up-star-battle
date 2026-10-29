"""Greedy Best-First cho Light Up (có lan truyền ràng buộc).

Lan truyền ràng buộc (các bước bắt buộc) và cách chọn ô theo MRV được tính
trong ``_propagate`` và ``_free_choices``.

Chỉ dùng ``h(n)`` để chọn nút mở rộng tiếp theo. ``h(n)`` là số ô trắng còn
chưa được chiếu sáng. Mỗi bóng đèn làm giảm đúng số ô này, nên nút nào chiếu
sáng được nhiều ô hơn sẽ được mở rộng trước.

Vì gốc là trạng thái sau lan truyền, ``path`` được bổ sung bàn cờ trống ở đầu
để ``path[0]`` luôn là bàn cờ chưa đặt gì.

    from src.model.light_up import LightUpProblem
    from src.heuristic.greedy.light_up import greedy

    problem = LightUpProblem.from_json("data/light_up/lu-7x7-normal-01.json")
    result = greedy(problem)
"""
from __future__ import annotations

import heapq

from src.model.light_up import LightUpProblem
from src.model.result import build_result, path_from_came_from


_NEIGHBOURS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _segments(problem: LightUpProblem) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Với mỗi ô trắng: các ô trắng cùng hàng/cột nhìn thấy nó (kể cả nó)."""
    out: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(problem.rows):
        for c in range(problem.cols):
            if problem.grid[r][c] != ".":
                continue
            cells = [(r, c)]
            for dr, dc in _NEIGHBOURS:
                rr, cc = r + dr, c + dc
                while (
                    0 <= rr < problem.rows
                    and 0 <= cc < problem.cols
                    and problem.grid[rr][cc] == "."
                ):
                    cells.append((rr, cc))
                    rr += dr
                    cc += dc
            out[(r, c)] = cells
    return out


def _free_choices(problem, segments, state, cell):
    """Các ô có thể đặt bóng đèn để chiếu sáng ``cell`` mà không đụng bóng khác."""
    out = []
    for r, c in segments[cell]:
        if (state[r] >> c) & 1:
            continue
        if any(
            0 <= r + dr < problem.rows
            and 0 <= c + dc < problem.cols
            and (state[r + dr] >> (c + dc)) & 1
            for dr, dc in _NEIGHBOURS
        ):
            continue
        out.append((r, c))
    return out


def _place(state, r, c):
    return state[:r] + (state[r] | (1 << c),) + state[r + 1:]


def _propagate(problem, segments, whites, state):
    """Áp dụng các bước bắt buộc. Trả về (state, ok)."""
    while True:
        lit = problem.illuminated_cells(state)
        unlit = whites - lit

        forced = None
        for cell in unlit:
            choices = _free_choices(problem, segments, state, cell)
            if not choices:
                return state, False
            if len(choices) == 1:
                forced = choices[0]
                break

        if forced is None:
            for r in range(problem.rows):
                for c in range(problem.cols):
                    clue = problem.grid[r][c]
                    if clue not in "01234":
                        continue
                    adj = [
                        (r + dr, c + dc)
                        for dr, dc in _NEIGHBOURS
                        if 0 <= r + dr < problem.rows
                        and 0 <= c + dc < problem.cols
                        and problem.grid[r + dr][c + dc] == "."
                    ]
                    placed = [(rr, cc) for rr, cc in adj if (state[rr] >> cc) & 1]
                    free = [p for p in adj if p not in placed]
                    need = int(clue) - len(placed)
                    if need < 0:
                        return state, False
                    if free and need == len(free):
                        forced = free[0]
                        break
                if forced is not None:
                    break

        if forced is None:
            return state, True

        state = _place(state, *forced)
        if not problem.is_valid_state(state):
            return state, False


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
