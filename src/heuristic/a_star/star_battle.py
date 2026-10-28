"""A* cho Star Battle.

Trạng thái dùng chung định dạng của repo: tuple bitmask, mỗi phần tử một hàng.
Nút gốc là bàn cờ trống, mỗi bước đặt đủ ``stars_per_unit`` ngôi sao cho hàng
còn thiếu đầu tiên.

``h(n) = số sao còn thiếu = stars_per_unit * rows - g``. Đây là chặn dưới đúng
(mỗi bước chỉ đặt được số sao của một hàng) nên A* không bao giờ bỏ qua lời giải
ngắn hơn. Vì ``f = g + h`` là hằng số, thứ tự mở rộng do tie-break quyết định:
ưu tiên nút mà hàng sắp xếp được ít lựa chọn nhất và ô đặt sao "ăn" được nhiều
ràng buộc nhất. Cách này giữ được tính đúng đắn của A* trong khi vẫn hút được
không gian tìm kiếm nhờ cắt nhánh của ``is_valid_state``.

Đường đi (``path``) được dựng bằng bảng ``came_from`` (mỗi nút một con trỏ cha)
rồi truy ngược từ goal, thay vì lưu cả đường đi trong từng nút.

    from src.model.star_battle import StarBattleProblem
    from src.heuristic.a_star.star_battle import a_star

    problem = StarBattleProblem.from_json("data/star_battle/sb-5x5-normal-01.json")
    result = a_star(problem)
"""
from __future__ import annotations

import heapq
from itertools import combinations

from src.model.result import build_result, path_from_came_from
from src.model.star_battle import StarBattleProblem


def _candidates(problem: StarBattleProblem, state: tuple[int, ...], row: int):
    """Các bộ cột có thể đặt đủ sao cho hàng ``row``, sắp theo độ "ăn" ràng buộc."""
    k = problem.stars_per_unit
    cols = problem.cols
    free = [
        c for c in range(cols)
        if not (state[row] >> c) & 1 and (row, c) not in problem.blocked_cells
    ]
    if len(free) < k:
        return []

    col_count = [0] * cols
    for mask in state:
        for c in range(cols):
            if (mask >> c) & 1:
                col_count[c] += 1
    region_count: dict[object, int] = {}
    if problem.regions is not None:
        for r, mask in enumerate(state):
            for c in range(cols):
                if (mask >> c) & 1:
                    rid = problem.regions[r][c]
                    region_count[rid] = region_count.get(rid, 0) + 1

    scored = []
    for combo in combinations(free, k):
        filled = 0
        ok = True
        seen_cols = set()
        for c in combo:
            if col_count[c] >= k or c in seen_cols:
                ok = False
                break
            seen_cols.add(c)
            filled += 1 if col_count[c] + 1 == k else 0
            if problem.regions is not None:
                rid = problem.regions[row][c]
                used = region_count.get(rid, 0) + sum(
                    1 for cc in combo if cc <= c and problem.regions[row][cc] == rid
                )
                if used > k:
                    ok = False
                    break
                if used == k:
                    filled += 1
        if ok:
            mask = 0
            for c in combo:
                mask |= 1 << c
            scored.append((filled, mask))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored


def a_star(problem: StarBattleProblem) -> dict:
    """A* trên Star Battle, trả về hợp đồng kết quả chung."""
    rows, cols, k = problem.rows, problem.cols, problem.stars_per_unit
    total = rows * k
    start: tuple[int, ...] = tuple([0] * rows)

    counter = 0
    heap = [(total, 0, 0, counter, start)]
    came_from: dict[tuple[int, ...], tuple[int, ...] | None] = {start: None}
    expanded = 0
    generated = 1
    peak = 1

    while heap:
        _, neg_fill, _, _, state = heapq.heappop(heap)
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

        for score, mask in _candidates(problem, state, row):
            nxt = state[:row] + (state[row] | mask,) + state[row + 1:]
            if nxt in came_from:
                continue
            if not problem.is_valid_state(nxt, partial=True):
                continue
            came_from[nxt] = state
            generated += 1
            g = sum(m.bit_count() for m in nxt)
            h = total - g
            counter += 1
            heapq.heappush(heap, (g + h, -score, h, counter, nxt))
            peak = max(peak, len(heap))

    return build_result(
        problem,
        expanded=expanded,
        generated=generated,
        frontier_peak=peak,
    )
