"""A* cho Light Up (có lan truyền ràng buộc).

Trạng thái là tuple bitmask (mỗi phần tử một hàng, bit = có bóng đèn), dùng
chung định dạng với ``LightUpProblem``.

Mỗi bước mở rộng: chọn một ô trắng **chưa được chiếu sáng**, thử đặt bóng đèn
vào một trong các ô cùng hàng/cột nhìn thấy được nó (kể cả chính nó). Mọi lời
giải hợp lệ đều phải chiếu sáng ô này bằng một trong các ô đó, nên không bỏ sót
nghiệm.

Trước khi mở rộng, mỗi trạng thái được lan truyền:
  (1) ô chưa sáng không còn chỗ đặt bóng đèn nào  -> nhánh vô nghiệm;
  (2) ô chưa sáng chỉ còn đúng một chỗ            -> đặt luôn (bước bắt buộc);
  (3) tường số còn thiếu n bóng và còn đúng n ô   -> đặt hết các ô đó.
Các bước bắt buộc không làm mất tính tối ưu vì chúng là hệ quả của ràng buộc.

``h(n) = ceil(số ô trắng chưa sáng / 5)``: một bóng đèn chiếu sáng tối đa 5 ô
nên còn ít nhất ``h(n)`` bóng phải đặt -> chặn dưới hợp lệ.

Vì gốc của cây tìm kiếm là trạng thái **sau khi lan truyền** (có thể đã có bóng
bắt buộc), ``path`` được bổ sung bàn cờ trống ở đầu để ``path[0]`` luôn là bàn
cờ chưa đặt gì.

    from src.model.light_up import LightUpProblem
    from src.heuristic.a_star.light_up import a_star

    problem = LightUpProblem.from_json("data/light_up/lu-7x7-normal-01.json")
    result = a_star(problem)
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


def a_star(problem: LightUpProblem) -> dict:
    """A* trên Light Up, trả về hợp đồng kết quả chung."""
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
        return -(-len(whites - problem.illuminated_cells(state)) // 5)

    counter = 0
    heap = [(h_of(start), 0, counter, start)]
    came_from: dict[tuple[int, ...], tuple[int, ...] | None] = {start: None}
    expanded = 0
    generated = 1
    peak = 1

    while heap:
        _, g, _, state = heapq.heappop(heap)
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
        target, choices = min(
            ((cell, _free_choices(problem, segments, state, cell)) for cell in unlit),
            key=lambda x: len(x[1]),
        )

        for r, c in choices:
            nxt, ok = _propagate(problem, segments, whites, _place(state, r, c))
            if not ok or nxt in came_from:
                continue
            came_from[nxt] = state
            generated += 1
            ng = g + sum(m.bit_count() for m in nxt) - sum(m.bit_count() for m in state)
            counter += 1
            heapq.heappush(heap, (ng + h_of(nxt), ng, counter, nxt))
            peak = max(peak, len(heap))

    return build_result(
        problem,
        expanded=expanded,
        generated=generated,
        frontier_peak=peak,
    )
