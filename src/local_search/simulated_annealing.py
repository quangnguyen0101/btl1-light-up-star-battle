"""Simulated Annealing cho Star Battle và Light Up (Chapter 3 -- Heuristic search).

Khác các thuật toán tìm kiếm có hệ thống (DFS, A*, Greedy): SA không duyệt cây.
Nó giữ **một** trạng thái hiện tại, thử một bước ngẫu nhiên, luôn nhận bước làm
năng lượng giảm, và nhận bước làm năng lượng tăng ``d`` với xác suất
``exp(-d / T)``. Khi ``T`` giảm dần, SA chuyển từ khám phá sang khai thác.

Năng lượng = tổng số vi phạm luật, bằng 0 khi và chỉ khi là lời giải:

- Star Battle: lệch số sao của mỗi cột và mỗi vùng, số cặp sao kề nhau (kể cả
  chéo), số sao đặt trên ô khoá. Mỗi hàng luôn có đúng ``stars_per_unit`` sao
  (bất biến), nên không cần đếm lệch theo hàng.
- Light Up: số ô trắng chưa được chiếu sáng, số cặp bóng nhìn thấy nhau, và
  tổng lệch số bóng so với mỗi tường số.

Bước đi: Star Battle chuyển một sao sang ô khác trong cùng hàng; Light Up bật
hoặc tắt bóng ở một ô trắng ngẫu nhiên.

Khi ``T`` xuống quá thấp, SA quay về trạng thái tốt nhất đã gặp và nung lại
(một chu kỳ mới). Hạt giống cố định nên kết quả tái lập được.

Kết quả: ``expanded`` và ``generated`` là số bước đã thử, ``frontier_peak`` luôn
là 1 (chỉ một trạng thái hiện tại). ``path`` chỉ ghi các trạng thái **cải thiện
kỷ lục** năng lượng, không ghi mọi bước đi; đó là chuỗi tiến triển từ bàn trống
tới đích, và đủ để ``validate_result`` chấp nhận.

    from src.model.light_up import LightUpProblem
    from src.local_search.simulated_annealing import simulated_annealing

    problem = LightUpProblem.from_json("data/light_up/lu-14x14-normal-01.json")
    result = simulated_annealing(problem)
"""
from __future__ import annotations

import math
import random

from src.model.light_up import LightUpProblem
from src.model.result import build_result, empty_state
from src.model.star_battle import StarBattleProblem

T0 = 1.0
ALPHA = 0.99995
CYCLE = 200_000


def _energy_star_battle(problem: StarBattleProblem, state) -> int:
    k = problem.stars_per_unit
    stars = [(r, c) for r, mask in enumerate(state) for c in range(problem.cols) if mask >> c & 1]
    star_set = set(stars)

    col_count = [0] * problem.cols
    for _, c in stars:
        col_count[c] += 1
    energy = sum(abs(n - k) for n in col_count)

    if problem.regions is not None:
        region_count: dict[object, int] = {}
        for r, c in stars:
            rid = problem.regions[r][c]
            region_count[rid] = region_count.get(rid, 0) + 1
        ids = {rid for row in problem.regions for rid in row}
        energy += sum(abs(region_count.get(rid, 0) - k) for rid in ids)

    energy += sum(1 for cell in stars if cell in problem.blocked_cells)

    for r, c in stars:
        for dr, dc in ((0, 1), (1, -1), (1, 0), (1, 1)):
            if (r + dr, c + dc) in star_set:
                energy += 1
    return energy


def _energy_light_up(problem: LightUpProblem, state, whites) -> int:
    bulbs = set(problem.coords_from_state(state))
    unlit = len(whites - problem.illuminated_cells(state))

    conflicts = 0
    for r, c in bulbs:
        for dr, dc in ((1, 0), (0, 1)):
            rr, cc = r + dr, c + dc
            while 0 <= rr < problem.rows and 0 <= cc < problem.cols and problem.grid[rr][cc] == ".":
                if (rr, cc) in bulbs:
                    conflicts += 1
                rr += dr
                cc += dc

    clue = 0
    for r in range(problem.rows):
        for c in range(problem.cols):
            cell = problem.grid[r][c]
            if cell in "01234":
                adjacent = sum(
                    (rr, cc) in bulbs
                    for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                    if 0 <= rr < problem.rows and 0 <= cc < problem.cols
                )
                clue += abs(adjacent - int(cell))

    return unlit + conflicts + clue


def _start_star_battle(problem: StarBattleProblem, rng: random.Random):
    cols = range(problem.cols)
    return tuple(
        sum(1 << c for c in rng.sample(cols, problem.stars_per_unit))
        for _ in range(problem.rows)
    )


def _move_star_battle(problem: StarBattleProblem, state, rng: random.Random):
    r = rng.randrange(problem.rows)
    mask = state[r]
    stars = [c for c in range(problem.cols) if mask >> c & 1]
    free = [c for c in range(problem.cols) if not mask >> c & 1]
    old, new = rng.choice(stars), rng.choice(free)
    moved = (mask & ~(1 << old)) | (1 << new)
    return state[:r] + (moved,) + state[r + 1:]


def _move_light_up(state, whites, rng: random.Random):
    r, c = rng.choice(whites)
    return state[:r] + (state[r] ^ (1 << c),) + state[r + 1:]


def simulated_annealing(problem, *, seed: int = 0, max_steps: int | None = None) -> dict:
    """SA trên Star Battle hoặc Light Up, trả về hợp đồng kết quả chung.

    ``max_steps`` (mặc định không giới hạn) chỉ dùng trong test để tránh chạy mãi
    trên đề vô nghiệm; ``scripts/run.py`` tự ngắt bằng timeout.
    """
    rng = random.Random(seed)
    empty = empty_state(problem)

    if isinstance(problem, StarBattleProblem):
        def energy(s):
            return _energy_star_battle(problem, s)

        def neighbour(s):
            return _move_star_battle(problem, s, rng)

        current = _start_star_battle(problem, rng)
    else:
        whites = [
            (r, c)
            for r in range(problem.rows)
            for c in range(problem.cols)
            if problem.grid[r][c] == "."
        ]
        white_set = set(whites)

        def energy(s):
            return _energy_light_up(problem, s, white_set)

        def neighbour(s):
            return _move_light_up(s, whites, rng)

        current = empty

    e_cur = energy(current)
    best, e_best = current, e_cur
    path = [empty, current]
    steps = 0
    cycle_step = 0
    temp = T0

    while e_best > 0 and (max_steps is None or steps < max_steps):
        steps += 1
        cycle_step += 1
        cand = neighbour(current)
        e_new = energy(cand)
        delta = e_new - e_cur
        if delta <= 0 or rng.random() < math.exp(-delta / temp):
            current, e_cur = cand, e_new
            if e_cur < e_best:
                best, e_best = current, e_cur
                path.append(best)

        temp *= ALPHA
        if cycle_step >= CYCLE:
            cycle_step = 0
            temp = T0
            current, e_cur = best, e_best

    if e_best == 0 and problem.is_goal(best):
        return build_result(
            problem,
            solution=problem.coords_from_state(best),
            path=path,
            expanded=steps,
            generated=steps,
            frontier_peak=1,
        )
    return build_result(
        problem,
        expanded=steps,
        generated=steps,
        frontier_peak=1,
    )
